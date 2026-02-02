import React from 'react';

const Feature: React.FC<{ title: string; children: React.ReactNode; icon: React.ReactNode }> = ({ title, children, icon }) => (
    <div className="flex">
        <div className="flex-shrink-0">
            <div className="flex items-center justify-center h-12 w-12 rounded-md bg-amber-500 text-white">
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
        <section id="features" className="py-20 bg-gray-50">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                <div className="lg:text-center">
                    <h2 className="text-base text-amber-500 font-semibold tracking-wide uppercase">Recovery Features</h2>
                    <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                        From Chaos to Order.
                    </p>
                    <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
                        Kintsu provides the tools you need to navigate the aftermath of a disaster and maximize your insurance claim.
                    </p>
                </div>

                <div className="mt-10">
                    <dl className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
                        <Feature title="Automated Claims Management" icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>}>
                            Track your claim status, deadlines, and communications in one centralized dashboard. Never miss a critical step in your recovery.
                        </Feature>
                        <Feature title="Inventory Recovery" icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>}>
                            Sync with Asset Guard to instantly generate proof of loss reports, or use our AI tools to reconstruct your inventory from photos and receipts post-disaster.
                        </Feature>
                        <Feature title="Expert Guidance" icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" /></svg>}>
                            Access a network of trusted public adjusters, contractors, and legal experts who specialize in disaster recovery.
                        </Feature>
                        <Feature title="Secure Document Vault" icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>}>
                            Keep all your critical documents—policy papers, receipts, correspondence—encrypted and safe, yet easily accessible when you need them most.
                        </Feature>
                    </dl>
                </div>
            </div>
        </section>
    );
};

export default Features;
