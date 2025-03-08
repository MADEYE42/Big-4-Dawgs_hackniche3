import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
    const [searchTerm, setSearchTerm] = useState('');

    const handleChange = (e) => {
        setSearchTerm(e.target.value);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (onSearch) {
            onSearch(searchTerm);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="flex items-center">
            <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={handleChange}
                className="border border-gray-300 rounded-l-md p-2 focus:outline-none focus:ring focus:border-blue-300"
            />
            <button
                type="submit"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-r-md focus:outline-none focus:shadow-outline"
            >
                Search
            </button>
        </form>
    );
};

export default SearchBar;