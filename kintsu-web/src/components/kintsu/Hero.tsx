import React from 'react';
import { Link } from 'react-router-dom';

const Hero: React.FC = () => {
    return (
        <section className="bg-white">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 flex flex-col items-center">
                <div className="max-w-3xl w-full text-center">
                    <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
                        <span className="block">Rebuild with</span>
                        <span className="block text-amber-500">Confidence.</span>
                    </h1>
                    <p className="mt-5 max-w-2xl mx-auto text-lg text-gray-500 md:text-xl">
                        Steps to recovery shouldn't be a mystery. Kintsu guides you through the complex insurance claims process, helping you recover specifically what you lost and get back to normal life faster.
                    </p>
                    <div className="mt-8 flex justify-center">
                        {/* "Get Support" button removed as requested */}
                    </div>
                </div>

                <div className="mt-12 w-full max-w-5xl">
                    <div className="w-full h-[400px] bg-gray-100 rounded-lg shadow-xl flex items-center justify-center overflow-hidden">
                        <img
                            className="w-full h-full object-cover"
                            src="/damaged_home.png"
                            alt="Interior of a home damaged by disaster, showing debris and structural damage."
                        />
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Hero;
