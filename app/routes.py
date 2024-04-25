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
    if not request.is_json:
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
    return new_user.to_dict()
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
# > FUNCTIONALIY: ADD VENDOR
@app.route('/vendors', methods=['POST'])
def add_vendor():
    # Make sure request body is json
    if not request.is_json:
        return {'Error':'Your content type must be application/json'}, 400
    # Get data from request body
    data = request.json
    # Validate is has req. fields
    required_fields = ['companyName', 'address']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Pull data from request body
    company_name = data.get('companyName')
    address = data.get('address')
  
    # Verify company name isn't already used
    check_vendors = db.session.execute(db.select(Vendor).where((Vendor.company_name == company_name))).scalars().all() 
    if check_vendors:
        return {'error': 'A user with that username and/or email already exists'}, 400

    # After checks, create user
    new_vendor = Vendor(company_name=company_name, address=address)
    return new_vendor.to_dict()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: DELETE VENDOR
@app.route('/vendors/<int:ven_id>', methods=['DELETE'])
def delete_vendor(ven_id):
    # Check if Vendor exists
    vendor = db.session.get(Vendor, ven_id)
    if vendor is None:
        return {'error': 'This user does not exists'}, 404
    vendor.delete()
    return {'success': f"User '{vendor.company_name} was deleted successfully."}, 200
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALITY: SEE ALL VENDORS
@app.route('/vendors')
def find_vendors():
    vendors = db.session.execute(db.select(Vendor)).scalars().all() 
    return [v.to_dict() for v in vendors]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALITY: GET TOKEN
    # ROADMAP ITEM: Allow vendor instances to be deleted via token auth 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


                                        # >>>> REVIEW ENDPOINTS <<<<<<


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: CREATE NEW REVIEW
@app.route('/reviews', methods=['POST'])
@token_auth.login_required
def create_review():
    # Req Obj must be json
    if not request.is_json:
        return {'error':'your content type must be application/json'}, 400
    data = request.json
    required_fields = ['vendor', 'title', 'body', 'rating']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error':f"{', '.join(missing_fields)} must be in the request body"}

    vendor = data.get('vendor')
    title = data.get('title')
    body = data.get('body')
    rating = data.get('rating')

    # Grab current user ID 
    current_user = token_auth.current_user() 
    # Grab vendor ID
    grabbed_vendor = db.session.execute(db.select(Vendor).filter_by(company_name=vendor)).scalar_one()
    # check_vendors = db.session.execute(db.select(Vendor).where((Vendor.company_name == vendor))).scalars().all() 
    # if check_vendors:
    #     grabbed_vendor = db.session.get(Vendor).where(Vendor.company_name == vendor)
    # else:
    #     return {'error': 'This vendor does not exist'}, 403

    new_review = Review(title=title, body=body, rating=rating, user_id=current_user.id, vendor_id=grabbed_vendor.id)
    return new_review.to_dict(), 201


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: SEE REVIEWS BY TITLE SEARCH
# @app.route('/reviews>')
# def search_vendor_reviews():
#     select_stmt = db.select(Review)
#     search = request.args.get('search')
#     if search:
#         select_stmt = select_stmt.where(Review.title.ilike(f"%{search}"))
#     reviews = db.session.execute(db.select(Review)).scalars().all()
#     return [r.to_dict() for r in reviews]
        
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: SEE ALL REVIEWS BY VENDOR COMPANY_NAME
@app.route('/reviews/<company_name>')
def get_vendor_reviews(company_name):
    grabbed_vendor = db.session.execute(db.select(Vendor).filter_by(company_name=company_name)).scalar_one()
    reviews = db.session.execute(db.select(Review).where((Review.vendor_id == grabbed_vendor.id))).scalars().all()
    if reviews:
        return [r.to_dict() for r in reviews]
    return f'This company currently has no reviews'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: SEE ALL REVIEWS BY USER ID -- NOT FUNCTIONING
@app.route('/reviews/<int:user_id>')
def get_user_reviews_by_ID(user_id):
    grabbed_user = db.session.execute(db.select(UserBuyer).where(UserBuyer.id==user_id)).scalar_one_or_none()
    reviews = db.session.execute(db.select(Review).where((Review.user_id == grabbed_user.id))).scalars().all()
    if reviews:
        return [r.to_dict() for r in reviews]
    return f'This company currently has no reviews'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: SEE ALL REVIEWS BY USERNAME -- NOT FUNCTIONING
@app.route('/reviews/<username>')
def get_user_reviews(username):
    user_reviews = db.session.execute(db.select(Review)).scalars().all()
    user_ids = db.session.execute(db.select(UserBuyer)).scalars().all()
    for r in user_reviews:
        if r.user_id in user_ids:
            rev = db.session.get(Review, r.user_id)
            return [r.to_dict() for r in rev]
    # grabbed_user = db.session.execute(db.select(UserBuyer).filter_by(username=username)).scalar_one_or_none()
    # user_reviews = db.session.execute(db.select(Review).where((Review.user_id == grabbed_user.id))).scalars().all()
    # if user_reviews:
        # return [r.to_dict() for r in user_reviews]
        else:
            return f'This user currently has no reviews'
    
# Make a join table? 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: UPDATE REVIEW
@app.route('/reviews/<int:review_id>', methods=['PUT'])
@token_auth.login_required
def edit_review(review_id):
    # Check to see that they have a json body
    if not request.is_json:
        return {'error':'Your content-type must be application/json'}, 400
    # find task by ID in database
    review = db.session.get(Review, review_id)
    if review is None:
        return {'error':'Review with an ID of #{review_id} does not exist'}, 404
    # Get current user based on token
    current_user = token_auth.current_user()
    #check if current user is author of task
    if current_user is not review.author:
        return {'error':"You do not have permission to edit this review"}, 403
    
    # Get data from Request:
    data = request.json
    # Pass that data into the task's update method
    review.update(**data)
    return review.to_dict() 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# > FUNCTIONALIY: DELETE REVIEW
@app.route('/reviews/<int:review_id>', methods=['DELETE'])
@token_auth.login_required
def delete_review(review_id):
    #check if the task exists 
    review = db.session.get(Review, review_id)
    if review is None:
        return {'error': 'This review does not exist'}, 404
    
    # make sure user trying to delete is the user whom create it 
    current_user = token_auth.current_user()
    if review.author is not current_user:
        return {'error':'You do not have permission to delete this review'}, 403 
    
    # delete task, calling delete method 
    review.delete()
    return {'success':f'{review.title} was deleted successfully'}, 200
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~