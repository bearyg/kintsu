import React from 'react';

const Hero: React.FC = () => {
    return (
        <section className="bg-white">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 flex flex-col items-center">
                <div className="max-w-3xl w-full text-center">
                    <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
                        <span className="block">Secure Your Tomorrow,</span>
                        <span className="block text-blue-600"> Today.</span>
                    </h1>
                    <p className="mt-5 max-w-2xl mx-auto text-lg text-gray-500 md:text-xl">
                        With AssetGuard, effortlessly catalog your home's valuables using AI. Be fully prepared for any insured disaster and ensure a smooth claims process. Peace of mind is just a few clicks away.
                    </p>
                    <div className="mt-8 flex justify-center">
                        <div className="rounded-md shadow">
                            <a href="#how-it-works" className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10 transition duration-150 ease-in-out">
                                Learn More
                            </a>
                        </div>
                    </div>
                </div>

                <div className="mt-12 w-full max-w-5xl">
                    <img
                        className="w-full h-auto max-h-[600px] object-cover rounded-lg shadow-xl"
                        src="/hero_image.png"
                        alt="Hero image for AssetGuard showing a well-organized and stylish living space."
                    />
                </div>
            </div>
        </section>
    );
};

export default Hero;
