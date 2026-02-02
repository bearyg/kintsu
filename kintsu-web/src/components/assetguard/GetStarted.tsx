import React from 'react';
import { UserIcon } from './icons/UserIcon';
import { DriveIcon } from './icons/DriveIcon';
import { SmartphoneIcon } from './icons/SmartphoneIcon';
import { EffortIcon } from './icons/EffortIcon';

const GetStarted: React.FC = () => {
    return (
        <section id="requirements" className="py-20 bg-gray-50">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center">
                    <h2 className="text-base text-blue-600 font-semibold tracking-wide uppercase">Requirements</h2>
                    <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                        What you'll need to get started.
                    </p>
                    <p className="mt-4 max-w-2xl text-xl text-gray-500 mx-auto">
                        To ensure a smooth and successful inventory process, please have the following ready.
                    </p>
                </div>

                <div className="mt-12 grid gap-10 md:grid-cols-2 lg:grid-cols-4 md:gap-x-8">
                    <div className="text-center">
                        <div className="flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 text-blue-600 mx-auto">
                            <UserIcon />
                        </div>
                        <h3 className="mt-6 text-xl font-bold text-gray-900">Google Account</h3>
                        <p className="mt-4 text-base text-gray-500">
                            A Google Account is required to log in and use the application securely.
                        </p>
                    </div>

                    <div className="text-center">
                        <div className="flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 text-blue-600 mx-auto">
                            <DriveIcon />
                        </div>
                        <h3 className="mt-6 text-xl font-bold text-gray-900">Google Drive Access</h3>
                        <p className="mt-4 text-base text-gray-500">
                            All your data is stored in your personal Google Drive, giving you full control and security.
                        </p>
                    </div>

                    <div className="text-center">
                        <div className="flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 text-blue-600 mx-auto">
                            <SmartphoneIcon />
                        </div>
                        <h3 className="mt-6 text-xl font-bold text-gray-900">Smartphone</h3>
                        <p className="mt-4 text-base text-gray-500">
                            You'll need a smartphone to capture photos, videos, and audio of your home and its contents.
                        </p>
                    </div>

                    <div className="text-center">
                        <div className="flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 text-blue-600 mx-auto">
                            <EffortIcon />
                        </div>
                        <h3 className="mt-6 text-xl font-bold text-gray-900">Time & Effort</h3>
                        <p className="mt-4 text-base text-gray-500">
                            The quality of your inventory depends on the quality of the data you provide. As they say, "garbage in, garbage out."
                        </p>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default GetStarted;
