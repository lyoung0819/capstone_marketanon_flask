from flask import request, render_template
from . import app, db
from .models import UserBuyer, Vendor, Review
from .auth import basic_auth, token_auth


                                    # >>>> HOME ENDPOINT <<<<<<
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/')
def index():
    return render_template('index.html')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                                    # >>>> USER/BUYER ENDPOINTS <<<<<<
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: CREATE USER
@app.route('/users', methods=['POST'])
def create_user():
    # Make sure request body is json
    if not request.id_json:
        return {'Error':'Your content type must be application/json'}, 400
    # Get data from request body
    data = request.json
    # Validate is has req. fields
    required_fields = ['firstName', 'lastName', 'username', 'email', 'title', 'company', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Pull data from request body
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email') 
    title = data.get('title') 
    company = data.get('company') 
    password = data.get('password') 

    # Verify username and email are unique
    check_users = db.session.execute(db.select(UserBuyer).where( (UserBuyer.username == username) | (UserBuyer.email == email) )).scalars().all() 
    if check_users:
        return {'error': 'A user with that username and/or email already exists'}, 400

    # After checks, create user
    new_user = UserBuyer(first_name=first_name, last_name=last_name, username=username, email=email, title=title, company=company, password=password)

    ###ROADMAP ITEM: Authenticating new user email with company SSO via openAuth?
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: DELETE USER
@app.route('/users/<int:user_id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(user_id):
    # Check if user exists
    user = db.session.get(UserBuyer, user_id)
    if user is None:
        return {'error': 'This user does not exists'}, 404
    # Authenticate user
    current_user = token_auth.current_user()
    if user is not current_user:
        return {'error': 'You do not have permission to delete this user.'}, 403
    # Delete user instance
    user.delete()
    return {'success': f"User '{user.first_name} was deleted successfully."}, 200
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCITONALITY: GET TOKEN 
@app.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    return user.get_token()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


                                    # >>>> VENDOR ENDPOINTS <<<<<<
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: DELETE VENDOR
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: DELETE VENDOR
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


                                        # >>>> REVIEW ENDPOINTS <<<<<<
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: CREATE NEW REVIEW
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: SEE ALL REVIEWS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: SEE REVIEW BY ID
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: UPDATE REVIEW
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: DELETE REVIEW
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~