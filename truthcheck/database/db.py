from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _seed_admin(app)

def _seed_admin(app):
    from models.user import User
    with app.app_context():
        if not User.query.filter_by(email='admin@truthcheck.ai').first():
            admin = User(
                username='admin',
                email='admin@truthcheck.ai',
                is_admin=True,
                is_active=True
            )
            admin.set_password('Admin@123!')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created: admin@truthcheck.ai / Admin@123!")
