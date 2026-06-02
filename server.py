import os
import sqlite3
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务端，命名为 DevContext
mcp = FastMCP("DevContext")
DB_PATH = os.path.join(os.path.dirname(__file__), "context.db")

def init_db():
    """初始化 SQLite 数据库，如果表不存在则创建"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # 创建存放代码片段的表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # 创建存放待办事项的表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 启动时确保数据库和表已经建立好
init_db()

@mcp.tool()
def save_code_snippet(title: str, content: str, tags: str = "") -> str:
    """
    Save a valuable code snippet, configuration, or note into the local database for future sessions.
    
    Args:
        title: The descriptive title of the code snippet.
        content: The actual code or note content.
        tags: Comma-separated tags for categorization (e.g., 'python,css').
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO snippets (title, content, tags) VALUES (?, ?, ?)",
            (title, content, tags)
        )
        conn.commit()
        conn.close()
        return f"Successfully saved snippet: '{title}'"
    except Exception as e:
        return f"Error saving snippet: {str(e)}"

@mcp.tool()
def search_snippets(keyword: str) -> str:
    """
    Search for previously saved code snippets or notes using a keyword.
    
    Args:
        keyword: The keyword to search for in titles, contents, or tags.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, content, tags FROM snippets WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return f"No snippets found matching keyword: '{keyword}'"
        
        result = []
        for row in rows:
            result.append(f"Title: {row[0]}\nTags: {row[2]}\nContent:\n{row[1]}\n---")
        return "\n\n".join(result)
    except Exception as e:
        return f"Error searching snippets: {str(e)}"

@mcp.tool()
def add_dev_todo(task: str, priority: str = "medium") -> str:
    """
    Add a new development task or todo item to the list.
    
    Args:
        task: The description of the task.
        priority: Task priority (low, medium, high).
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO todos (task, priority) VALUES (?, ?)",
            (task, priority)
        )
        conn.commit()
        conn.close()
        return f"Successfully added todo: '{task}' with {priority} priority."
    except Exception as e:
        return f"Error adding todo: {str(e)}"

@mcp.tool()
def list_pending_todos() -> str:
    """
    List all pending development tasks and todo items.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, priority FROM todos WHERE status = 'pending'")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "No pending todos found. Great job!"
        
        result = ["Pending Todo List:"]
        for row in rows:
            result.append(f"[{row[0]}] ({row[2].upper()}) {row[1]}")
        return "\n".join(result)
    except Exception as e:
        return f"Error listing todos: {str(e)}"

if __name__ == "__main__":
    mcp.run()