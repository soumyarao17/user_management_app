# User Management System with Role-Based Access Control


Output/Screenshots -
-----------------
1. The password is stored in the form of a hash in the database, to avoid direct exposure to any user:
<img width="1389" alt="Screenshot 2023-09-27 at 9 17 07 PM" src="https://github.com/ayushraj-in/accessMangement/assets/47022604/e2f57115-dd3b-4417-a295-05622ae141da">

2. All the user actions including logging, registration, CRUD Operations, and permission granting/revoking are logged in the database as follows:
<img width="1379" alt="Screenshot 2023-09-27 at 9 19 22 PM" src="https://github.com/ayushraj-in/accessMangement/assets/47022604/b2900b18-bcdd-4f93-82e8-c7208285dcdd">

3. Tasks and Notes are stored in different tables with their respective title and content.
<img width="269" alt="Screenshot 2023-09-27 at 9 19 59 PM" src="https://github.com/ayushraj-in/accessMangement/assets/47022604/9673ac13-706b-4f2d-a3c1-41b7bbb84d16">


Code flow -
----------------------
1. app/management/commands/access_manager.py -> Implementation of the command line interface (CLI) for performing core functions such as registration, logging in/out, displaying options, permissions, tasks/notes, navigate_from_options etc.
2. app/management/constants.py -> All the possible constants across the access_manager.py file.
3. app/management/constants.py -> All the possible constants across all files.
3. app/models.py -> UserManager, User, UserActionLog, Task, Note models with validations and related functions
4. app/models/user_utils.py -> All the functions for implementing logging, registration, CRUD operations and permission granting/revoking by the admin etc. 


Execution Setup -
-----------------
1. Download and extract the zip file.

2. Download and install MySQL or install via Terminal - brew install MySQL

3. Start MySQL server: brew services start MySQL

4. (Optional) Set MySQL Password, MySQL Root Password

5. Install Docker and start the Docker daemon

6. Host MySQL server on Docker container and expose it to port 3306. Use commands - <br />
(Ensure you are in the project home directory)<br />
Build - docker build -f docker/db/Dockerfile -t user_management_db . <br />
Run - docker run --network=host -it --expose 3306 -p 3306:3306 user_management_db<br />

7. MySQL server is now hosted which automatically creates database "user_management_db"
(If you have set MySQL Root Password, update the Dockerfile accordingly)

8. Build and run docker for user management commands:<br />
Build - docker build -f docker/cli/Dockerfile -t user_management_system . <br />
Run - docker run --network=host -it --expose 8000 -p 8000:8000 user_management_system <br />

9. Open Docker Desktop and run a terminal in the user_management_system container
								<br /> OR <br />
	docker images | grep user_management_system # Copy id     <br />
	docker run -i -t <id> /bin/bash      <br />

10. Testing and Output:
- Run the command: 'python manage.py access_manager'
- Home Page: Choose from options R, LI, LO, -1 to perform the desired operation <br />
   		a) Options: <br /> R. Register - New User Registration - (By default the first user is assigned as the admin, who can then grant/revoke permission to others)
  	       <br />LI. Login - Existing User Login 
               <br />LO. Logout - User Log out
               <br />-1. Exit - Exit Program <br />
						     
  <img width="523" alt="image" src="https://github.com/ayushraj-in/accessMangement/assets/47022604/3a1f1aef-df31-4f3e-83ed-8b77f91146a3"><br />
  <img width="699" alt="image" src="https://github.com/ayushraj-in/accessMangement/assets/47022604/9fb70e58-4629-4650-92a5-4afb0bda4abe"><br />

- Enter 'username' and 'password' during logging in or registration stage. Also, add whether you are an "Admin" or not.
- Choose from options: <br />N. Notes - To perform operations on notes
                       <br />T. Tasks - To perform operations on notes
                       <br />A. Admin Panel - To grant/revoke addition/deletion/updation/view access to other users
                       <br />HP. Home Page - To return to Home Page
                       <br />LO. Logout - To log out of the account
                       <br />-1. Exit - Exit Program <br/>
		       
  <img width="432" alt="image" src="https://github.com/ayushraj-in/accessMangement/assets/47022604/1f9df795-b549-4a85-b36d-0fb5ebf3e03e">


- Notes: <br />ND. Show Note Detail - To show the detail of a note by its id
         <br />CN. Create Note - To create a new note
         <br />UN. Update Note - To update the contents of a note
         <br />DN. Delete Note - To delete a note <br/>
  
  <img width="540" alt="image" src="https://github.com/ayushraj-in/accessMangement/assets/47022604/2be3c5b2-72a1-47ec-92eb-d9ce99ca54f8">


- Tasks: <br />TD. Show Task Detail - To show the detail of a task by its id
         <br />CT. Create Task - To create a new task
         <br />UT. Update Task - To update the contents of a task
         <br />DT. Delete Task - To delete a task <br/>
	 
<img width="611" alt="image" src="https://github.com/ayushraj-in/accessMangement/assets/47022604/f07dfa4a-0251-48b9-8646-783fc4509032">

- Admin Panel: <br />V_A. Add/Remove view access - To grant or revoke view access to/from a user
               <br />U_A. Add/Remove update access - To grant or revoke update access to/from a user
               <br />A_A. Add/Remove add access - To grant or revoke add access to/from a user
               <br />D_A. Add/Remove delete access - To grant or revoke delete access to/from a user
               <br />The user can then further choose the resource whose permission needs to be updated, the username of the user and the access option (add or delete) to perform permission based operations. <br/>
	       
  <img width="490" alt="image" src="https://github.com/ayushraj-in/accessMangement/assets/47022604/bfbc73fa-b666-4cbb-a4b4-42883d816bd1"><br/>
  <img width="438" alt="image" src="https://github.com/ayushraj-in/accessMangement/assets/47022604/63a56e38-1a24-460c-883e-8e656598c8aa"><br/>

