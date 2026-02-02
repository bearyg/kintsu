import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
    return (
        <header className="bg-white shadow-sm sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex">
                        <div className="flex-shrink-0 flex items-center">
                            <Link to="/" className="text-2xl font-bold text-gray-900">
                                Homestead<span className="text-blue-600">Inventory</span>
                            </Link>
                        </div>
                    </div>
                    <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                        <Link
                            to="/asset-guard"
                            className="border-transparent text-gray-500 hover:border-blue-500 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                        >
                            Asset Guard
                        </Link>
                        <Link
                            to="/kintsu"
                            className="border-transparent text-gray-500 hover:border-amber-500 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                        >
                            Kintsu
                        </Link>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
