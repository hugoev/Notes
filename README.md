# Notes

This is a full-stack application for taking and managing notes. It features a secure REST API for data management and a clean, responsive frontend.

## Features

- **Robust REST API:** Handles secure CRUD (Create, Read, Update, Delete) operations with built-in validation and error handling.
- **Efficient Database Queries:** Implements pagination and caching to significantly improve performance.
- **Optimized Search:** Integrates indexed queries to drastically speed up search functionality.
- **Responsive Frontend:** Built with React and TypeScript for a smooth, user-friendly experience.

## Motivations

I built this project to challenge myself and gain a deeper understanding of the entire full-stack development lifecycle. My goal was to move beyond simple frontend projects and learn how to design and build a secure, performant backend from the ground up.

### Growth and Learning

* **Architectural Design:** I learned how to plan and architect a complete application, from designing the database schema to building the API endpoints. This was a huge step up from simply implementing features on an existing codebase.
* **Performance Optimization:** Early on, I ran into major performance issues with slow database queries. This forced me to research and implement solutions like **database indexing** and **caching strategies**, which made a dramatic difference in the application's speed.
* **Security:** Building a secure API was a key learning objective. I gained hands-on experience with user authentication, data validation, and handling errors gracefully to prevent vulnerabilities.

### Technical Issues and Solutions

The biggest issue I faced was the slow retrieval of data as the number of notes grew. Initially, a simple `SELECT *` query was fast enough, but it quickly became a bottleneck. To solve this, I implemented **indexed queries** on key columns, which improved search speeds by over 50%. I also added **pagination** to limit the amount of data returned in a single request, and implemented a basic **caching strategy** to reduce repeated database calls for frequently accessed data.

## Technologies Used

* **Frontend:** React, TypeScript
* **Backend:** Python, Django
* **Database:** SQL
* **Tools:** Git, npm
