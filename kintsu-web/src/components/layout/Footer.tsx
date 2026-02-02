import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
    return (
        <footer className="bg-gray-50 border-t border-gray-200">
            <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
                <div className="md:flex md:items-center md:justify-between">
                    <div className="flex justify-center md:order-2 space-x-6">
                        <Link to="/privacy" className="text-gray-400 hover:text-gray-500">
                            Privacy Policy
                        </Link>
                        <Link to="/terms" className="text-gray-400 hover:text-gray-500">
                            Terms of Service
                        </Link>
                    </div>
                    <div className="mt-8 md:mt-0 md:order-1">
                        <p className="text-center text-base text-gray-400">
                            &copy; {new Date().getFullYear()} HomesteadInventory.com. All rights reserved.
                        </p>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
