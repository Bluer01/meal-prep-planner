# Meal Prep Planner

A simple web application to help plan your meal prep by calculating ingredients needed for multiple recipes.

## Features

- Store and manage recipes with ingredients
- Select multiple recipes for meal prep
- Automatically calculate total ingredients needed
- Add new recipes through a user-friendly interface
- Persistent storage of recipes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/meal-prep-planner.git
cd meal-prep-planner
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python run.py
```

5. Visit http://localhost:5000 in your web browser

## Development

To set up the development environment:

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Run linting:
```bash
flake8
black .
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/name`)
3. Commit your changes (`git commit -am 'Add feature'`)
4. Push to the branch (`git push origin feature/name`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.