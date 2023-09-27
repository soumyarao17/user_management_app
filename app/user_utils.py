from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from app.models import Task, Note, UserActionLog
from django.utils import timezone
from app.constants import RoleChoices
import logging

from app.settings import LOG_DIR

logger = logging.getLogger(__name__)
User = get_user_model()


def log_user_action(user, action, error=False, **kwargs):
    app = kwargs.get('app', 'app')
    log_text = f'{timezone.now()} : {user.username} performed "{action}" at {app} : {kwargs.get("details")}'
    if error:
        logger.error(log_text)
    else:
        logger.info(log_text)
    details = kwargs.get('details', '')
    details = details + ' ' + log_text
    UserActionLog.objects.create(user=user, action=action, details=details)


def log_permission_change():
    def decorator(func):
        def wrapper(*args, **kwargs):
            res, uname = args[0], args[1]
            guarantor = kwargs.get('guarantor', 'system')
            try:
                user = User.objects.get(username=uname)
            except Exception:
                return ValueError(f"No user exists with uname: {uname}")

            previous_perms = user.get_user_permissions()
            updated_perms = set(func(*args, **kwargs).get_user_permissions())
            added_perms = updated_perms - previous_perms
            removed_perms = previous_perms - updated_perms
            for added_perm in added_perms:
                action, app = added_perm.split('.')[-1].split('_')
                log_user_action(user, action, app, details=f'Granted {added_perm} permission to {uname} by {guarantor}')
            for removed_perm in removed_perms:
                action, app = removed_perm.split('.')[-1].split('_')
                log_user_action(user, action, app,
                                details=f'Revoked {removed_perm} permission to {uname} by {guarantor}')

        return wrapper

    return decorator


def log_signin_attempts(action):
    def decorator(func):
        def log(uname, text, is_error):
            user = User.objects.get(username=uname)
            log_user_action(user, action, error=is_error, details=text)

        def wrapper(*args, **kwargs):
            uname = kwargs.get('username') or args[0]
            try:
                user = func(*args, **kwargs)
            except User.DoesNotExist:
                raise ValueError(f"Matching user does not exist for uname: {uname}")
            except Exception as e:
                log(uname, str(e), True)
                raise e
            login_success = True if user else False
            log(uname, f'Logged in - {login_success}', False)
            return user

        return wrapper

    return decorator


def grant_default_resource_permissions(user):
    for resource in ['task', 'note']:
        for access in ['view', 'add', 'change', 'delete']:
            if access != 'view' and not user.is_admin:
                continue
            permission = Permission.objects.get(codename=f'{access}_{resource}')
            user.user_permissions.add(permission)
            logger.info(f'Permission granted to user "{user.username}" to view {resource} at {timezone.now()}')


@log_permission_change()
def add_user_permission(resource, uname, access, **kwargs):
    user = User.objects.get(username=uname)
    permission = Permission.objects.get(codename=f'{access}_{resource}')
    user.user_permissions.add(permission)
    user.save()
    return user


@log_permission_change()
def remove_user_permission(resource, uname, access, **kwargs):
    user = User.objects.get(username=uname)
    permission = Permission.objects.get(codename=f'{access}_{resource}')
    user.user_permissions.remove(permission)
    user.save()
    return user


@log_signin_attempts('register')
def register_user(username, password, is_admin):
    try:
        role = RoleChoices.ADMIN if is_admin else RoleChoices.USER
        user = User.objects.create_user(username=username, password=password, role=role)
        grant_default_resource_permissions(user)
        if user.log_in(password):
            logger.info(f'User "{username}" registered at {timezone.now()}')
            return user
        raise ValueError(f'Post Registration Log In failed. Please retry!')
    except Exception as e:
        raise ValueError(f'Registration failed: {e}')


@log_signin_attempts('login')
def login_user(username, password):
    user = User.objects.get(username=username)
    if user.log_in(password):
        logger.info(f'User "{username}" logged in at {timezone.now()}')
        return user
    else:
        raise ValueError('Login failed. Check your username and password.')


@log_signin_attempts('logout')
def logout_user(username):
    user = User.objects.get(username=username)
    if not user.log_out():
        raise ValueError('Logout failed!')


def resource_permission_required(resource_access):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = args[0]
            action, app = resource_access.split('.')[-1].split('_')
            if not user.has_perm(resource_access):
                # print(user.get_all_permissions(), resource_access)
                text = 'Insufficient permission to perform the operation'
                log_user_action(user, action, app=app, details=text, error=True)
                raise PermissionDenied(text)
            _value = func(*args, **kwargs)

            text = _value.get('log_text', '')
            log_user_action(user, action, app=app, details=text)
            return _value

        return wrapper

    return decorator


def get_user_permissions(user, resource):
    access_scopes = set()
    for perm in user.get_all_permissions():
        access, res = perm.split('.')[-1].split('_')
        if res == resource:
            access_scopes.add(access)
    return list(access_scopes)


@resource_permission_required('app.view_task')
def task_list(_):
    tasks = Task.objects.all()
    return {'value': list(tasks) or [], 'log_text': f'Task list retrieved at {timezone.now()}'}


@resource_permission_required('app.view_task')
def task_detail(_, task_id):
    task = get_object_or_404(Task, pk=task_id)
    return {'value': {'title': task.title, 'content': task.content}, 'log_text': f'Task detail retrieved for note ID '
                                                                                 f'{task_id} at {timezone.now()}'}


@resource_permission_required('app.add_task')
def task_create(_, data):
    title = data.get('title')
    content = data.get('content')
    if title:
        task = Task(title=title, content=content)
        task.save()
        return {'value': '', 'log_text': f'Task created with title "{title}" at {timezone.now()}'}


@resource_permission_required('app.change_task')
def task_edit(_, data):
    task_id = data.get('task_id')
    title = data.get('title')
    content = data.get('content')
    task = Task.objects.filter(pk=task_id).first()
    if not task:
        return {'value': '', 'log_text': 'You don\'t have permission to edit this task.'}

    if title:
        task.title = title
        task.content = content
        task.save()
        return {'value': '', 'log_text': f'Task with ID {task_id} edited at {timezone.now()}'}


@resource_permission_required('app.delete_task')
def task_delete(_, task_id):
    task = Task.objects.filter(pk=task_id).first()
    if not task:
        return {'value': '', 'log_text': 'You don\'t have permission to delete this task.'}

    task.delete()
    return {'value': '', 'log_text': f'Task with ID {task_id} deleted at {timezone.now()}'}


@resource_permission_required('app.view_note')
def note_list(_):
    notes = Note.objects.all() or []
    return {'value': list(notes), 'log_text': f'Note list retrieved at {timezone.now()}'}


@resource_permission_required('app.view_note')
def note_detail(_, note_id):
    note = get_object_or_404(Note, pk=note_id)
    return {'value': {'title': note.title, 'content': note.content}, 'log_text': f'Note detail retrieved for note ID '
                                                                                 f'{note_id} at {timezone.now()}'}


@resource_permission_required('app.add_note')
def note_create(_, data):
    title = data.get('title')
    content = data.get('content')
    if title:
        note = Note(title=title, content=content)
        note.save()
        return {'value': '', 'log_text': f'Note created with title "{title}" at {timezone.now()}'}


@resource_permission_required('app.change_note')
def note_edit(_, data):
    note_id = data.get('note_id')
    title = data.get('title')
    content = data.get('content')
    note = Note.objects.filter(pk=note_id).first()
    if not note:
        return {'value': '', 'log_text': 'You don\'t have permission to edit this note.'}

    if title:
        note.title = title
        note.content = content
        note.save()
        return {'value': '', 'log_text': f'Note with ID {note_id} edited at {timezone.now()}'}


@resource_permission_required('app.delete_note')
def note_delete(_, note_id):
    note = Note.objects.filter(pk=note_id).first()
    if not note:
        return {'value': '', 'log_text': 'You don\'t have permission to delete this note.'}

    note.delete()
    return {'value': '', 'log_text': f'Note with ID {note_id} deleted at {timezone.now()}'}


def create_db():
    import mysql.connector
    try:
        mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
        )
        db_name = "user_management_db"

        cursor = mydb.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        open(f'{LOG_DIR}/user_actions.log', 'a+')

        return True
    except mysql.connector.Error as err:
        print('Something went wrong: {}'.format(err))
    except Exception as ex:
        print("Exception: {}".format(ex))
    return False
