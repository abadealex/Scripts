# smartscripts/app/main.py

from fastapi import FastAPI
from smartscripts.app.teacher.routes import router as teacher_router
from smartscripts.app.student.routes import router as student_router
from smartscripts.app.auth.routes import router as auth_router

app = FastAPI(title="SmartScripts API")

# Register routers with appropriate prefixes
app.include_router(auth_router, prefix="/api/auth")
app.include_router(teacher_router, prefix="/api/teacher")
app.include_router(student_router, prefix="/api/student")


@app.get("/")
async def root():
    return {"message": "Welcome to SmartScripts API"}
