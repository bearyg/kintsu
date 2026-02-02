import React from 'react';

const Terms: React.FC = () => {
    return (
        <div className="bg-white py-16 px-4 overflow-hidden sm:px-6 lg:px-8 lg:py-24">
            <div className="relative max-w-xl mx-auto">
                <div className="text-center">
                    <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                        Terms of Service
                    </h2>
                    <p className="mt-4 text-lg leading-6 text-gray-500">
                        Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
                    </p>
                </div>
                <div className="mt-12">
                    <div className="prose prose-blue prose-lg text-gray-500 mx-auto">
                        <h3>1. Service Description and Purpose</h3>
                        <ul>
                            <li>
                                <strong>Free Service:</strong> The application is provided to you free of charge at this time and may be discontinued at any time.
                            </li>
                            <li>
                                <strong>Purpose:</strong> The service's sole purpose is to process files you designate and return the results to you within your Google Drive.
                            </li>
                        </ul>

                        <h3>2. Google Drive Access and Authorization</h3>
                        <ul>
                            <li>
                                <strong>Required Access:</strong> To use the service, you must grant the application permission to read, process, and write files within a specific, dedicated directory and its sub-directories that it creates in your Google Drive.
                            </li>
                            <li>
                                <strong>User Responsibility:</strong> You are responsible for all files you place into this dedicated directory. Do not place files you do not wish the application to process into this location. We are not responsible for the contents or security of the data residing in your Google Drive.
                            </li>
                        </ul>

                        <h3>3. User Obligations and Prohibited Uses</h3>
                        <p>
                            You agree not to use the application for any purpose that is unlawful or prohibited by these Terms, including but not limited to:
                        </p>
                        <ul>
                            <li>Uploading or processing files that contain illegal content.</li>
                            <li>Uploading or processing files that infringe on any third party’s intellectual property rights (copyrights, trademarks, etc.).</li>
                            <li>Attempting to use the application to gain unauthorized access to any system or network.</li>
                        </ul>

                        <h3>4. Disclaimer of Warranties</h3>
                        <p>
                            The application is provided on an "AS IS" and "AS AVAILABLE" basis. We make no warranties, expressed or implied, regarding the operation or availability of the application. We do not warrant that the application will be uninterrupted, error-free, or completely secure.
                        </p>

                        <h3>5. Limitation of Liability</h3>
                        <p>
                            In no event shall the application creator be liable for any indirect, incidental, special, consequential, or punitive damages, including but not limited to loss of profits, data, goodwill, or other intangible losses, resulting from: (i) your use of or inability to use the service; (ii) any unauthorized access to or use of your Google Drive directory; or (iii) any errors or omissions in the service.
                        </p>

                        <h3>6. Termination</h3>
                        <p>
                            We reserve the right to suspend or terminate your access to the application at any time, without prior notice, if you breach these Terms of Service.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Terms;
