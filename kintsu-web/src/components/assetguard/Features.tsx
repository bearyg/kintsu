import React from 'react';

const Feature: React.FC<{ title: string; children: React.ReactNode; icon: React.ReactNode }> = ({ title, children, icon }) => (
    <div className="flex">
        <div className="flex-shrink-0">
            <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-600 text-white">
                {icon}
            </div>
        </div>
        <div className="ml-4">
            <dt className="text-lg leading-6 font-medium text-gray-900">{title}</dt>
            <dd className="mt-2 text-base text-gray-500">{children}</dd>
        </div>
    </div>
);

const Features: React.FC = () => {
    return (
        <section id="features" className="py-20 bg-white">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <div className="lg:text-center">
                    <h2 className="text-base text-blue-600 font-semibold tracking-wide uppercase">Features</h2>
                    <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                        Everything you need to be prepared.
                    </p>
                    <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
                        AssetGuard is packed with features designed to make your home inventory process fast, accurate, and secure.
                    </p>
                </div>

                <div className="mt-10">
                    <dl className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
                        <Feature title="Multi-Media Uploads" icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>}>
                            Securely upload photos, videos, and audio descriptions for a rich, detailed record of your belongings. Our system handles various formats with ease.
                        </Feature>
                        <Feature title="AI-Powered Valuation" icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v.01" /></svg>}>
                            Leverage the power of Google's Gemini to get up-to-date replacement values, grounded in real-world data from online retailers.
                        </Feature>
                        <Feature title="Comprehensive Reporting" icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>}>
                            Export your entire inventory to a universally compatible spreadsheet, perfect for sharing with your insurance agent or for your personal records.
                        </Feature>
                        <Feature title="Verifiable Sources" icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>}>
                            Every valuation includes a direct link to the source, providing full transparency and making it easy to verify the information.
                        </Feature>
                        <Feature title="Secure Cloud Storage" icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>}>
                            Your inventory data is stored securely in your own Google Drive. AssetGuard doesn't store your data, giving you complete control and the industry-leading security of Google.
                        </Feature>
                    </dl>
                </div>
            </div>
        </section>
    );
};

export default Features;
