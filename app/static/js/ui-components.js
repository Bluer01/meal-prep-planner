const CategoryFilter = ({ categories, onChange }) => {
    const [filterType, setFilterType] = React.useState('OR');

    const handleChange = (selectedCategories) => {
        onChange(selectedCategories, filterType);
    };

    return React.createElement('div', {
        className: 'space-y-4'
    }, [
        React.createElement('div', {
            className: 'flex items-center space-x-4 mb-4',
            key: 'filter-type'
        }, [
            React.createElement('span', {
                className: 'text-sm font-medium text-gray-700',
                key: 'label'
            }, 'Filter Type:'),
            React.createElement('select', {
                value: filterType,
                onChange: (e) => setFilterType(e.target.value),
                className: 'border border-gray-300 rounded-md shadow-sm p-2 text-sm',
                key: 'select'
            }, [
                React.createElement('option', { value: 'OR', key: 'or' }, 'Match Any (OR)'),
                React.createElement('option', { value: 'AND', key: 'and' }, 'Match All (AND)')
            ])
        ]),
        React.createElement('div', {
            className: 'flex flex-wrap gap-2',
            key: 'categories'
        }, Array.from(categories).map(category => 
            React.createElement('label', {
                key: category,
                className: 'inline-flex items-center p-2 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors cursor-pointer'
            }, [
                React.createElement('input', {
                    type: 'checkbox',
                    value: category,
                    onChange: (e) => {
                        const checkboxes = document.querySelectorAll('#categoryFilters input:checked');
                        const selected = Array.from(checkboxes).map(cb => cb.value);
                        handleChange(selected);
                    },
                    className: 'form-checkbox h-4 w-4 text-blue-600 rounded border-gray-300',
                    key: `checkbox-${category}`
                }),
                React.createElement('span', {
                    className: 'ml-2 text-sm text-gray-700',
                    key: `text-${category}`
                }, category)
            ])
        ))
    ]);
};

// Export the component
window.CategoryFilter = CategoryFilter;