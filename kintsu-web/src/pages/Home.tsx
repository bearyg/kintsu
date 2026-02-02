import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
    return (
        <div className="bg-white">
            {/* Hero Section */}
            <div className="relative bg-gray-900 overflow-hidden">
                <div className="absolute inset-0">
                    <img
                        className="w-full h-full object-cover"
                        src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=60"
                        alt="Secure home interior"
                    />
                    <div className="absolute inset-0 bg-gray-900 opacity-75"></div>
                </div>
                <div className="relative max-w-7xl mx-auto py-24 px-4 sm:py-32 sm:px-6 lg:px-8">
                    <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl text-center">
                        Homestead Inventory
                    </h1>
                    <p className="mt-6 text-xl text-gray-300 max-w-3xl mx-auto text-center">
                        Complete protection for your home's legacy. From proactive preparation to compassionate recovery.
                    </p>
                </div>
            </div>

            {/* Products Section */}
            <div className="py-16 bg-gray-50 overflow-hidden lg:py-24">
                <div className="relative max-w-xl mx-auto px-4 sm:px-6 lg:px-8 lg:max-w-7xl">
                    <div className="relative">
                        <h2 className="text-center text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                            Two Powerful Solutions
                        </h2>
                        <p className="mt-4 max-w-3xl mx-auto text-center text-xl text-gray-500">
                            Whether you're planning ahead or rebuilding, we have the specialized tools you need.
                        </p>
                    </div>

                    <div className="relative mt-12 lg:mt-24 lg:grid lg:grid-cols-2 lg:gap-8 lg:items-center">
                        {/* Asset Guard Card */}
                        <div className="relative group bg-white p-6 rounded-2xl shadow-xl transition-all hover:shadow-2xl hover:-translate-y-1">
                            <div className="absolute -top-10 left-1/2 transform -translate-x-1/2">
                                <div className="p-4 bg-blue-600 rounded-2xl shadow-lg">
                                    <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                            </div>
                            <div className="mt-8 text-center">
                                <h3 className="text-2xl font-bold text-gray-900 tracking-tight">Asset Guard</h3>
                                <p className="mt-4 text-lg text-gray-500">
                                    Secure your tomorrow, today. Effortlessly catalog your valuables using AI to ensure you're fully prepared for any insured disaster.
                                </p>
                                <div className="mt-8">
                                    <Link
                                        to="/asset-guard"
                                        className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                                    >
                                        Prepare with Asset Guard
                                    </Link>
                                </div>
                            </div>
                        </div>

                        {/* Kintsu Card */}
                        <div className="relative mt-20 lg:mt-0 group bg-white p-6 rounded-2xl shadow-xl transition-all hover:shadow-2xl hover:-translate-y-1">
                            <div className="absolute -top-10 left-1/2 transform -translate-x-1/2">
                                <div className="p-4 bg-amber-500 rounded-2xl shadow-lg">
                                    <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                    </svg>
                                </div>
                            </div>
                            <div className="mt-8 text-center">
                                <h3 className="text-2xl font-bold text-gray-900 tracking-tight">Kintsu</h3>
                                <p className="mt-4 text-lg text-gray-500">
                                    Rebuild with confidence. Turn chaos into order after a disaster with automated claims management and inventory recovery.
                                </p>
                                <div className="mt-8">
                                    <Link
                                        to="/kintsu"
                                        className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-amber-500 hover:bg-amber-600"
                                    >
                                        Recover with Kintsu
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;
