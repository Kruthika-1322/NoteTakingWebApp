from fastapi import FastAPI, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import bcrypt
import re
from models import User, Note
from database import SessionLocal, create_tables
from mangum import Mangum

# Create the tables
create_tables()
current_user_id = None

# FastAPI application
app = FastAPI()
handler = Mangum(app)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def validate_email(email: str):
    if not re.match(r"[^@]+@gmail\.com$", email):
        raise HTTPException(status_code=400, detail="Invalid email address. Must be a Gmail address.")

def validate_password(password: str):
    if (len(password) < 6 or
        not re.search(r"[A-Z]", password) or
        not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)):
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long, contain one uppercase letter, and one special character.")

@app.get("/", response_class=RedirectResponse)
async def read_root():
    return RedirectResponse(url="/signin.html")

@app.get("/signin.html")
def sign_in(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})

@app.post("/signin.html")
async def sign_in_post(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    global current_user_id
    # Validate email format
    try:
        validate_email(email)
    except HTTPException as e:
        return templates.TemplateResponse("signin.html", {"request": request, "error": e.detail})

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return templates.TemplateResponse("signin.html", {"request": request, "error": "Account not registered. Please sign up."})

    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return templates.TemplateResponse("signin.html", {"request": request, "error": "Incorrect password."})
    current_user_id = user.id
    print(f"The user_is is in signin: {current_user_id}")


    return RedirectResponse(url="/index.html", status_code=303)  # Redirect to index.html

@app.get("/signup.html")
def sign_up(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup.html")
async def sign_up_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    global current_user_id
    try:
        validate_email(email)
        validate_password(password)
    except HTTPException as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error": e.detail})

    existing_email_user = db.query(User).filter(User.email == email).first()
    if existing_email_user:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Email already registered."})

    existing_username_user = db.query(User).filter(User.username == username).first()
    if existing_username_user:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already taken."})

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    new_user = User(username=username, email=email, password=hashed_password.decode("utf-8"))
    db.add(new_user)
    db.commit()
    current_user_id = new_user.id
    print(f"The user_is is in signup : {current_user_id}")

    return RedirectResponse(url="/index.html", status_code=303)  # Redirect to index.html

@app.get("/forgot_password.html")
def forgot_password(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.post("/forgot_password.html")
async def forgot_password_post(
    request: Request,
    email: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Validate the email format
        validate_email(email)
        # Validate the new password against criteria
        validate_password(new_password)
    except HTTPException as e:
        return templates.TemplateResponse("forgot_password.html", {"request": request, "error": e.detail})

    # Check if the new password matches the confirmation password
    if new_password != confirm_password:
        return templates.TemplateResponse("forgot_password.html", {"request": request, "error": "Passwords do not match."})

    # Retrieve the user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return templates.TemplateResponse("forgot_password.html", {"request": request, "error": "Email not found."})

    # Check if the new password is the same as the previous password
    if bcrypt.checkpw(new_password.encode('utf-8'), user.password.encode('utf-8')):
        return templates.TemplateResponse("forgot_password.html", {"request": request, "error": "New password cannot be the same as the old password."})

    # Hash the new password and update the user's password in the database
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password.decode('utf-8')
    db.commit()

    # Show success message
    return templates.TemplateResponse("forgot_password.html", {"request": request, "success": "Password updated successfully."})


@app.get("/index.html")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/save_note")
async def save_note(
    request: Request,
    db: Session = Depends(get_db)
):
    note_data = await request.json()

    note_id = note_data.get('id')
    user_id = note_data.get('user_id')
    content = note_data.get('content')

    # Validate data
    if not note_id or not user_id or not content:
        raise HTTPException(status_code=400, detail="Missing required fields")
    existing_note = db.query(Note).filter(Note.id == note_id).first()
    if existing_note:
        return {"status": "info", "message": "Note with this ID already exists. No new note created."}

    # Save the note to the database
    new_note = Note(id=note_id, content=content, user_id=user_id)
    db.add(new_note)
    db.commit()

    return {"status": "success", "message": "Note saved successfully!"}


@app.get("/get_username")
async def get_username(db: Session = Depends(get_db)):
    global current_user_id
    print(f"The user_is is in get username : {current_user_id}")# Use the global user_id variable

    if current_user_id is None:
        raise HTTPException(status_code=401, detail="User not logged in")

    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username, "user_id": user.id}  # Return both username and user_id

@app.delete("/delete_note")
async def delete_note(request: Request, db: Session = Depends(get_db)):
    note_data = await request.json()
    note_id = note_data.get('id')

    if note_id:
        note = db.query(Note).filter(Note.id == note_id).first()
        if note:
            db.delete(note)
            db.commit()
            return {"status": "success", "message": "Note deleted successfully!"}

    return {"status": "error", "message": "Note not found"}

@app.get("/get_notes/{user_id}")
async def get_notes(user_id: str, db: Session = Depends(get_db)):
    notes = db.query(Note).filter(Note.user_id == user_id).all()
    return [{"id": note.id, "content": note.content, "timestamp": note.id} for note in notes]

@app.put("/update_note")
async def update_note(
    request: Request,
    db: Session = Depends(get_db)
):
    note_data = await request.json()
    note_id = note_data.get('id')
    content = note_data.get('content')

    # Validate data
    if not note_id or not content:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Find the note by ID and update its content
    note = db.query(Note).filter(Note.id == note_id).first()
    if note:
        note.content = content
        db.commit()
        return {"status": "success", "message": "Note updated successfully!"}
    else:
        raise HTTPException(status_code=404, detail="Note not found")
