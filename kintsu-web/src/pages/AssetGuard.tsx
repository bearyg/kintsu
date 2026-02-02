import React from 'react';
import Hero from '../components/assetguard/Hero';
import HowItWorks from '../components/assetguard/HowItWorks';
import Features from '../components/assetguard/Features';
import GetStarted from '../components/assetguard/GetStarted';
import InventoryManager from '../components/assetguard/InventoryManager';

const AssetGuard: React.FC = () => {
    return (
        <>
            <Hero />
            <HowItWorks />
            <Features />
            <GetStarted />
            <InventoryManager />
        </>
    );
};

export default AssetGuard;
