# **Agent-Library**

The Agent-Library repository contains an innovative AI-powered library management system designed to streamline the organization and accessibility of books and resources. This project aims to provide an efficient and user-friendly interface for managing library operations, including cataloging, borrowing, and retrieving information about books.

## 🚀 Features

- **Book Cataloging:** Allows for easy addition and management of book entries with details such as title, author, publication date, and ISBN.
- **Borrowing System:** Enables users to borrow and return books with automated due dates and reminders.
- **Search Functionality:** Provides a robust search feature to find books by title, author, or ISBN efficiently.
- **User Management:** Supports multiple user roles (admin, librarian, borrower) with different permissions for managing library operations.
- **AI-Powered Recommendations:** Utilizes machine learning algorithms to suggest books based on users' borrowing history and preferences.

## 📬 Contact Me

Feel free to reach out for collaborations, opportunities, or just a tech chat!

- 📧 [Email Id](mailto:erkrishbhimani@gmail.com)  
- 🔗 [LinkedIn Profile](https://www.linkedin.com/in/krishbhimani/)

## 🕠️ Installation

### 1 Clone the Repository

```sh
git clone https://github.com/KrishBhimani/Agent-Library.git
```

### 2 Create a Virtual Environment

#### For Windows:
```sh
conda create -p venv python==3.11 -y
conda activate venv/
```

#### For macOS/Linux:
```sh
python3 -m venv venv
source venv/bin/activate
```

### 3 Install Dependencies

```sh
pip install -r requirements.txt
```

### 4 Run the Application

```sh
python app.py
```

## 📌 Usage

1. **Initial Setup:** After cloning and installing dependencies, run the application and follow the on-screen instructions to set up the database and create an admin account.
2. **Adding Books:** Use the admin interface to add books, specifying details like title, author, and ISBN.
3. **Borrowing Books:** Users can search for books and borrow them. The system automatically tracks borrowing history and due dates.
4. **Returning Books:** Users can return books, and the system updates the book's status and notifies the user about any fines.

## 🔧 Technologies Used

- **Backend:** Python 3.11, Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** SQLite
- **AI/ML:** TensorFlow, Scikit-learn
- **Development Tools:** Git, VSCode

## 🚀 Challenges & Solutions

- **Challenge:** Integrating AI-powered recommendation features without significantly impacting performance.
  - **Solution:** Implemented asynchronous processing for recommendation algorithms to ensure a seamless user experience.
- **Challenge:** Ensuring data consistency and integrity across different user interactions.
  - **Solution:** Utilized transactions in database operations to maintain data integrity.

## 🤝 Contributing

Contributions are welcome! Feel free to submit **issues** or **pull requests** to improve this project.

---