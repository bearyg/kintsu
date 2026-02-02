import React from 'react';

const Privacy: React.FC = () => {
    return (
        <div className="bg-white py-16 px-4 overflow-hidden sm:px-6 lg:px-8 lg:py-24">
            <div className="relative max-w-xl mx-auto">
                <div className="text-center">
                    <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                        Privacy Policy
                    </h2>
                    <p className="mt-4 text-lg leading-6 text-gray-500">
                        Last updated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
                    </p>
                </div>
                <div className="mt-12">
                    <div className="prose prose-blue prose-lg text-gray-500 mx-auto">
                        <h3>1. Information We Access and Process</h3>
                        <p>
                            Our application is designed to operate on files you explicitly place within a specific folder it creates in your Google Drive (including its sub-directories).
                        </p>
                        <ul>
                            <li>
                                <strong>Google Drive Access:</strong> We request access to your Google Drive for the sole purpose of accessing, processing, and storing the results within the designated folder and its sub-directories.
                            </li>
                            <li>
                                <strong>Data Processing:</strong> The application processes the contents of the files in the designated directory to generate results for your use.
                            </li>
                            <li>
                                <strong>Data Storage:</strong> We store the results of the processing within your designated Google Drive folder.
                            </li>
                            <li>
                                <strong>No Content Retention:</strong> We do not maintain or store information regarding the contents of your original files outside of the processing time required to generate the results. We do not retain copies of your data on our servers.
                            </li>
                        </ul>

                        <h3>2. Information We Collect (User Data)</h3>
                        <ul>
                            <li>
                                <strong>Minimal User Data:</strong> At this time, we intentionally collect minimal to no personal identifying information about our users.
                            </li>
                            <li>
                                <strong>Operational Logs:</strong> We may maintain diagnostic or operational logs on our servers that could potentially include non-identifying information like timestamps, IP addresses, and application-specific error codes. This data is used strictly for maintaining application performance, diagnosing technical issues, and security.
                            </li>
                        </ul>

                        <h3>3. Data Sharing and Disclosure</h3>
                        <p>We respect your privacy.</p>
                        <ul>
                            <li>
                                <strong>No Sharing or Selling:</strong> We do not share, sell, rent, or trade any data to which we have access—including your Google Drive file contents, processing results, or operational logs—with any third-party businesses or organizations.
                            </li>
                            <li>
                                <strong>Legal Exceptions:</strong> The only exceptions would be if we are legally required to do so by law, court order, or governmental regulation.
                            </li>
                        </ul>

                        <h3>4. Data Security</h3>
                        <p>
                            We implement reasonable security measures designed to protect the limited data we do access and process. However, no security system is impenetrable, and we cannot guarantee the absolute security of our operational logs or the data on your Google Drive.
                        </p>

                        <h3>5. Changes to This Privacy Policy</h3>
                        <p>
                            We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Privacy;
