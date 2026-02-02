import React from 'react';

const InventoryManager: React.FC = () => {
    return (
        <section id="inventory-tool" className="py-20 bg-gray-50">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <div className="max-w-3xl mx-auto">
                    <h2 className="text-center text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">Create Your Inventory</h2>
                    <p className="mt-4 text-center text-xl text-gray-500">
                        Use our live application to start your home inventory.
                    </p>

                    <div className="text-center my-8 p-6 bg-blue-50 border-l-4 border-blue-500 rounded-r-lg shadow-sm">
                        <p className="text-lg text-gray-800 mb-4">
                            This application is deployed and ready to use. Click the button below to start creating your inventory on the live site.
                        </p>
                        <a
                            href="https://asset-guard-gcp.web.app/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 shadow-md transition duration-150 ease-in-out transform hover:scale-105"
                            aria-label="Go to the live AssetGuard application"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                            Go to Live Application
                        </a>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default InventoryManager;
