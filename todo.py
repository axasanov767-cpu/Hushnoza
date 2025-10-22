class Todo:
    def __init__(self,todo_name, description, priority, date):
        self.todo_name = todo_name
        self.description = description
        self.prioritiy = priority
        self.data = date
        self.completed = False

    def mark_completed(self):
        self.completed = True

    def __str__(self):
        status = "True" if self.completed else "False"
        return f"{status} {self.todo_name} {self.description} Peioritet: {self.priority} Sana: {self.date}"
    

class App:
    def __init__(self, name):
        self.name = name
        self.todos = []

    def create_todo(self, todo_name, description, priority, date):
        todo = Todo(todo_name, description, priority, date)
        self.todos.append(todo)
        print(f"Todo qo`shildi: {todo_name}")

    def todo_list(self):
        if not self.todos:
            print("Todo royhati bosh")
        else:
            print("\nTodo royhati: ")
            for idx, todo in enumerate(self.todos, start = 1):
                print(f"{idx}. {todo}")

    def complete_todo(self, index):
        if 0 <= index < len(self.todos):
            self.todos[index].mark_completed()
            print(f"{self.todos[index].todo_name} bajarildi !")
        else:
            print("Bunday index mavjud emas")

    def delete_todo(self, index):
        if 0 <= index < len(self.todos):
            removed = self.todos.pop(index)
            print(f"{removed.todo_name} o`chirildi")
        else:
            print("Bunday index mavjud emas")

