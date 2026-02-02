import React from 'react';
import { CameraIcon } from './icons/CameraIcon';
import { AnalyzeIcon } from './icons/AnalyzeIcon';
import { ReportIcon } from './icons/ReportIcon';

const HowItWorks: React.FC = () => {
    return (
        <section id="how-it-works" className="py-20 bg-gray-50">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center">
                    <h2 className="text-base text-blue-600 font-semibold tracking-wide uppercase">How It Works</h2>
                    <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                        A simple, powerful process.
                    </p>
                    <p className="mt-4 max-w-2xl text-xl text-gray-500 mx-auto">
                        We've streamlined the home inventory process into three easy steps.
                    </p>
                </div>

                <div className="mt-12 grid gap-10 md:grid-cols-3 md:gap-x-8 md:gap-y-12">
                    <div className="text-center">
                        <div className="flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 text-blue-600 mx-auto">
                            <CameraIcon />
                        </div>
                        <h3 className="mt-6 text-xl font-bold text-gray-900">1. Capture Your Assets</h3>
                        <p className="mt-4 text-base text-gray-500">
                            Walk through your home, room by room, and upload photos or videos. You can also record audio notes to describe specific items in more detail.
                        </p>
                    </div>

                    <div className="text-center">
                        <div className="flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 text-blue-600 mx-auto">
                            <AnalyzeIcon />
                        </div>
                        <h3 className="mt-6 text-xl font-bold text-gray-900">2. AI-Powered Analysis</h3>
                        <p className="mt-4 text-base text-gray-500">
                            Our advanced AI, powered by Gemini, analyzes your media to automatically identify, categorize, and find the current replacement value for each item.
                        </p>
                    </div>

                    <div className="text-center">
                        <div className="flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 text-blue-600 mx-auto">
                            <ReportIcon />
                        </div>
                        <h3 className="mt-6 text-xl font-bold text-gray-900">3. Get Your Report</h3>
                        <p className="mt-4 text-base text-gray-500">
                            Receive a detailed spreadsheet with your complete inventory, item values, and links to both your original media and the pricing sources used by the AI.
                        </p>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default HowItWorks;
