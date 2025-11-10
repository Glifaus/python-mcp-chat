"""Seed script to populate database with example data."""
from app.database import SessionLocal, init_db
from app import crud


def seed():
    """Seed the database with example data."""
    print("🌱 Seeding database...")
    
    init_db()
    db = SessionLocal()
    
    try:
        # Mensajes en diferentes canales
        print("📨 Creating messages in different channels...")
        msg1 = crud.send_message(db, "Alice", "¡Hola a todos! 👋", "general")
        print(f"  ✅ Message {msg1} created in #general")
        
        msg2 = crud.send_message(db, "Bob", "¿Alguien usa Python?", "python")
        print(f"  ✅ Message {msg2} created in #python")
        
        msg3 = crud.send_message(db, "Charlie", "Busco desarrollador Python", "jobs")
        print(f"  ✅ Message {msg3} created in #jobs")
        
        msg4 = crud.send_message(db, "Diana", "Nuevo proyecto con FastAPI 🚀", "python")
        print(f"  ✅ Message {msg4} created in #python")
        
        msg5 = crud.send_message(db, "Eve", "¿Alguien para jugar?", "general")
        print(f"  ✅ Message {msg5} created in #general")
        
        # Threads (respuestas)
        print("\n🧵 Creating threads (replies)...")
        reply1 = crud.reply_to_message(db, msg1, "Bob", "¡Hola Alice! ¿Qué tal?")
        print(f"  ✅ Reply {reply1} added to message {msg1}")
        
        reply2 = crud.reply_to_message(db, msg1, "Charlie", "¡Hola! Bienvenida 😊")
        print(f"  ✅ Reply {reply2} added to message {msg1}")
        
        reply3 = crud.reply_to_message(db, msg2, "Alice", "Yo uso Python todos los días")
        print(f"  ✅ Reply {reply3} added to message {msg2}")
        
        reply4 = crud.reply_to_message(db, msg2, "Diana", "Python es genial para backend")
        print(f"  ✅ Reply {reply4} added to message {msg2}")
        
        reply5 = crud.reply_to_message(db, msg4, "Bob", "FastAPI es increíble!")
        print(f"  ✅ Reply {reply5} added to message {msg4}")
        
        # Reacciones
        print("\n😊 Adding reactions...")
        crud.add_reaction(db, msg1, "Bob", "👍")
        print(f"  ✅ Reaction 👍 added to message {msg1}")
        
        crud.add_reaction(db, msg1, "Charlie", "❤️")
        print(f"  ✅ Reaction ❤️ added to message {msg1}")
        
        crud.add_reaction(db, msg1, "Diana", "👏")
        print(f"  ✅ Reaction 👏 added to message {msg1}")
        
        crud.add_reaction(db, msg2, "Alice", "🐍")
        print(f"  ✅ Reaction 🐍 added to message {msg2}")
        
        crud.add_reaction(db, msg2, "Diana", "👍")
        print(f"  ✅ Reaction 👍 added to message {msg2}")
        
        crud.add_reaction(db, msg4, "Bob", "🚀")
        print(f"  ✅ Reaction 🚀 added to message {msg4}")
        
        crud.add_reaction(db, msg4, "Alice", "🔥")
        print(f"  ✅ Reaction 🔥 added to message {msg4}")
        
        crud.add_reaction(db, msg4, "Charlie", "💯")
        print(f"  ✅ Reaction 💯 added to message {msg4}")
        
        print("\n✅ Database seeded successfully!")
        print(f"\n📊 Summary:")
        print(f"  - {5} messages created")
        print(f"  - {5} replies created")
        print(f"  - {8} reactions added")
        print(f"  - {3} channels: #general, #python, #jobs")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
