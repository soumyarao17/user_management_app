from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management.base import BaseCommand
from django.core.management import call_command

from app.user_utils import login_user, note_list, task_list, note_create, note_detail, note_edit, \
    note_delete, task_detail, task_create, task_edit, task_delete, add_user_permission, create_db, get_user_permissions, \
    remove_user_permission, logout_user

from app.management.constants import REGISTER_USER_OPTION, HOME_PAGE, LOGGED_IN_PAGE, EXIT_USER_OPTION, NOTES_PAGE, \
    TASKS_PAGE, TASKS, NOTES, LOGIN_USER_OPTION, NOTE_DETAIL, CREATE_NOTE, UPDATE_NOTE, DELETE_NOTE, TASK_DETAIL, \
    CREATE_TASK, UPDATE_TASK, DELETE_TASK, ADMIN_PANEL_OPTION, ADMIN_PAGE, VIEW_ACCESS, UPDATE_ACCESS, ADD_ACCESS, \
    DELETE_ACCESS, HOME_PAGE_OPTION, LOGOUT_USER_OPTION


class Command(BaseCommand):
    help = 'User management program from the command line'
    user = None
    min_length = 8
    min_digit_count = 1
    min_special_char_count = 1

    def validate(self, password):
        if len(password) < self.min_length:
            raise ValidationError(
                "The password must be at least {min_length} characters long.".format(min_length=self.min_length),
                code='password_too_short',
            )

        if sum(1 for char in password if char.isdigit()) < self.min_digit_count:
            raise ValidationError(
                "The password must contain at least {min_digit_count} digit(s).".format(
                    min_digit_count=self.min_digit_count),
                code='password_no_digit',
            )

        if sum(1 for char in password if not char.isalnum()) < self.min_special_char_count:
            raise ValidationError(
                "The password must contain at least {min_special_char_count} special character(s).".format(
                    min_special_char_count=self.min_special_char_count),
                code='password_no_special_char',
            )

    def register(self):
        username = input('Enter a username: ')
        password = input('Enter a password: ')
        is_admin = input('Is admin[y/n] (Optional): ')

        self.validate(password)
        if is_admin and is_admin in ['y', 'Y']:
            is_admin = True
        else:
            is_admin = False

        try:
            from app.user_utils import register_user
            user = register_user(username, password, is_admin)
            self.stdout.write(self.style.SUCCESS(f'User "{username}" successfully registered.'))
            return user
        except ValueError as e:
            self.stdout.write(self.style.ERROR(str(e)))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
        return None

    def login(self):
        username = input('Enter a username: ')
        password = input('Enter a password: ')

        try:
            user = login_user(username, password)
            self.stdout.write(self.style.SUCCESS(f'User "{username}" successfully logged in.'))
            return user
        except ValueError as e:
            self.stdout.write(self.style.ERROR(str(e)))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
        return None

    def logout(self):
        try:
            logout_user(self.user)
            self.stdout.write(self.style.SUCCESS("Logged out successfully!"))
            self.user = None
        except ValueError as e:
            self.stdout.write(self.style.ERROR(str(e)))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
        return None

    def intro(self):
        self.stdout.write(f"------------------------------------")
        self.stdout.write(f"USER MANAGEMENT SYSTEM BY SOUMYA RAO")
        self.stdout.write(f"------------------------------------")

    def show_options(self, page):
        if page == HOME_PAGE:
            self.stdout.write(f"{REGISTER_USER_OPTION}. Register")
            self.stdout.write(f"{LOGIN_USER_OPTION}. Login")
        elif page == LOGGED_IN_PAGE:
            self.stdout.write(f"{NOTES}. Notes")
            self.stdout.write(f"{TASKS}. Tasks")
            if self.user and self.user.is_admin:
                self.stdout.write(f"{ADMIN_PANEL_OPTION}. Admin Panel")
            self.stdout.write(f"{HOME_PAGE_OPTION}. Home Page")
        elif page == ADMIN_PAGE:
            self.stdout.write(f"{VIEW_ACCESS}. Add/Remove view access")
            self.stdout.write(f"{UPDATE_ACCESS}. Add/Remove update access")
            self.stdout.write(f"{ADD_ACCESS}. Add/Remove add access")
            self.stdout.write(f"{DELETE_ACCESS}. Add/Remove delete access")
            self.stdout.write(f"{HOME_PAGE_OPTION}. Home Page")
        elif page == NOTES_PAGE:
            self.show_app_permissions(self.user, 'note')
            self.show_notes()
            self.stdout.write(f"{NOTE_DETAIL}. Show Note Detail")
            self.stdout.write(f"{CREATE_NOTE}. Create Note")
            self.stdout.write(f"{UPDATE_NOTE}. Update Note")
            self.stdout.write(f"{DELETE_NOTE}. Delete Note")
            self.stdout.write(f"{HOME_PAGE_OPTION}. Home Page")
        elif page == TASKS_PAGE:
            self.show_app_permissions(self.user, 'task')
            self.show_tasks()
            self.stdout.write(f"{TASK_DETAIL}. Show Task Detail")
            self.stdout.write(f"{CREATE_TASK}. Create Task")
            self.stdout.write(f"{UPDATE_TASK}. Update Task")
            self.stdout.write(f"{DELETE_TASK}. Delete Task")
            self.stdout.write(f"{HOME_PAGE_OPTION}. Home Page")
        else:
            self.stdout.write(self.style.ERROR("Yet to write"))
        self.stdout.write(f"{LOGOUT_USER_OPTION}. Logout")
        self.stdout.write(f"{EXIT_USER_OPTION}. Exit")

    def show_app_permissions(self, user, resource):
        all_perms = ",".join(get_user_permissions(user, resource))
        print('USER PERMISSIONS:', all_perms)

    def show_notes(self):
        notes = note_list(self.user)['value']
        for note in notes:
            print(note)

    def show_tasks(self):
        tasks = task_list(self.user)['value']
        for task in tasks:
            print(task)

    def handle(self, *args, **options):
        status = create_db()
        if status:
            call_command('makemigrations', 'app')
            call_command('migrate', 'app')

            if options.get('import'):
                call_command('importDb')
            self.execute_manager()
        else:
            print('DB Creation failed!')

    def execute_manager(self):
        page = HOME_PAGE
        self.intro()

        while True:
            try:
                self.show_options(page)
                option = input('Choose an OPTION: ')

                if option == EXIT_USER_OPTION:
                    break
                if option == HOME_PAGE_OPTION:
                    page = HOME_PAGE
                    continue
                page = self.navigate_from_options(page, option)
            except PermissionDenied as e:
                self.stdout.write(self.style.ERROR(str(e)))
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
            for _ in range(2):
                self.stdout.write("")

    def navigate_from_options(self, page, option):
        if option == REGISTER_USER_OPTION:
            page = self.execute_register(page)
        if option == LOGIN_USER_OPTION:
            page = self.execute_login(page)
        if option == LOGOUT_USER_OPTION:
            self.logout()
            page = HOME_PAGE
        if option == ADMIN_PANEL_OPTION:
            page = ADMIN_PAGE
        if option == NOTES:
            page = NOTES_PAGE
        if option == TASKS:
            page = TASKS_PAGE
        if option == NOTE_DETAIL:
            note_id = input('Enter Note ID: ')
            detail = note_detail(self.user, note_id)
            print(f"Your requested note details are: Title: {detail['value']['title']} Content: "
                  f"{detail['value']['content']}")
            page = NOTES_PAGE
        if option == CREATE_NOTE:
            title = input('Enter Title: ')
            content = input('Enter Content: ')
            note_create(self.user, {'title': title, 'content': content})
            page = NOTES_PAGE
        if option == UPDATE_NOTE:
            note_id = input('Enter Note ID: ')
            title = input('Enter New Title: ')
            content = input('Enter New Content: ')
            note_edit(self.user, {'note_id': note_id, 'title': title, 'content': content})
            page = NOTES_PAGE
        if option == DELETE_NOTE:
            note_id = input('Enter Note ID: ')
            note_delete(self.user, note_id)
            page = NOTES_PAGE
        if option == TASK_DETAIL:
            task_id = input('Enter Task ID: ')
            detail = task_detail(self.user, task_id)
            print(f"Your requested task details are: Title: {detail['value']['title']} Content: "
                  f"{detail['value']['content']}")
            page = TASKS_PAGE
        if option == CREATE_TASK:
            title = input('Enter Title: ')
            content = input('Enter Content: ')
            task_create(self.user, {'title': title, 'content': content})
            page = TASKS_PAGE
        if option == UPDATE_TASK:
            task_id = input('Enter Task ID: ')
            title = input('Enter New Title: ')
            content = input('Enter New Content: ')
            task_edit(self.user, {'task_id': task_id, 'title': title, 'content': content})
            page = TASKS_PAGE
        if option == DELETE_TASK:
            task_id = input('Enter Task ID: ')
            task_delete(self.user, task_id)
            page = TASKS_PAGE
        if option == VIEW_ACCESS:
            resource, uid, option = self.get_details_for_access()
            if option == 'add':
                add_user_permission(resource, uid, 'view', guarantor=self.user)
            elif option == 'delete':
                remove_user_permission(resource, uid, 'view', guarantor=self.user)
            else:
                self.stdout.write(self.style.ERROR(f'Please choose from valid options: add, delete'))
            self.stdout.write(self.style.SUCCESS(f'Success!'))
            page = ADMIN_PAGE
        if option == UPDATE_ACCESS:
            resource, uid, option = self.get_details_for_access()
            if option == 'add':
                add_user_permission(resource, uid, 'change', guarantor=self.user)
            elif option == 'delete':
                remove_user_permission(resource, uid, 'change', guarantor=self.user)
            else:
                self.stdout.write(self.style.ERROR(f'Please choose from valid options: add, delete'))
            self.stdout.write(self.style.SUCCESS(f'Success!'))
            page = ADMIN_PAGE
        if option == ADD_ACCESS:
            resource, uid, option = self.get_details_for_access()
            if option == 'add':
                add_user_permission(resource, uid, 'add', guarantor=self.user)
            elif option == 'delete':
                remove_user_permission(resource, uid, 'add', guarantor=self.user)
            else:
                self.stdout.write(self.style.ERROR(f'Please choose from valid options: add, delete'))
            self.stdout.write(self.style.SUCCESS(f'Success!'))
            page = ADMIN_PAGE
        if option == DELETE_ACCESS:
            resource, uid, option = self.get_details_for_access()
            if option == 'add':
                add_user_permission(resource, uid, 'delete', guarantor=self.user)
            elif option == 'delete':
                remove_user_permission(resource, uid, 'delete', guarantor=self.user)
            else:
                self.stdout.write(self.style.ERROR(f'Please choose from valid options: add, delete'))
            self.stdout.write(self.style.SUCCESS(f'Success!'))
            page = ADMIN_PAGE
        return page

    @staticmethod
    def get_details_for_access():
        resource, uid, option = None, None, None
        resources = ['note', 'task']
        options = ['add', 'delete']
        while resource not in resources:
            print(f'Please chose from: {", ".join(resources)}')
            resource = input('Enter Resource Name: ')
        uid = input('Enter username to add: ')
        option = input(f'Choose access option - {", ".join(options)}: ')
        return resource, uid, option

    def execute_register(self, page):
        user = self.register()
        if user:
            self.user = user
            return LOGGED_IN_PAGE
        else:
            print('Failed! Try again!')
        return page

    def execute_login(self, page):
        user = self.login()
        if user:
            self.user = user
            page = LOGGED_IN_PAGE
        else:
            print("Invalid Login!")
        return page
