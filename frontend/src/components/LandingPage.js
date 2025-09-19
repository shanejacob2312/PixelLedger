import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Upload, Search, CheckCircle, Lock, Eye, Zap } from 'lucide-react';

const LandingPage = () => {
  const features = [
    {
      icon: Shield,
      title: 'Semantic-Aware Watermarking',
      description: 'Uses AI models (BLIP + ResNet) to extract visual context and embed semantic features into your images.',
    },
    {
      icon: Lock,
      title: 'Tamper Detection',
      description: 'Detects subtle forgery through semantic drift analysis and perceptual hash comparison.',
    },
    {
      icon: Eye,
      title: 'Invisible Watermarks',
      description: 'LSB-based embedding ensures watermarks are invisible to the human eye while maintaining image quality.',
    },
    {
      icon: Zap,
      title: 'Blockchain Ready',
      description: 'Generates blockchain-ready payloads for immutable ownership verification and authenticity.',
    },
  ];

  const steps = [
    {
      number: '1',
      title: 'Upload Image',
      description: 'Upload your image and let our AI extract semantic context automatically.',
    },
    {
      number: '2',
      title: 'Add Metadata',
      description: 'Provide ownership details, copyright information, and other metadata.',
    },
    {
      number: '3',
      title: 'Create Watermark',
      description: 'Our system embeds a semantic watermark with tamper detection capabilities.',
    },
    {
      number: '4',
      title: 'Verify Authenticity',
      description: 'Verify watermarked images anytime to check authenticity and detect tampering.',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 to-primary-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Protect Your Digital Assets with{' '}
              <span className="text-gradient">Semantic Watermarking</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              PixelLedger uses advanced AI models to create invisible, tamper-resistant watermarks 
              that embed semantic context and ownership information directly into your images.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/create" className="btn-primary text-lg px-8 py-3">
                <Upload className="w-5 h-5 mr-2 inline" />
                Create Watermark
              </Link>
              <Link to="/verify" className="btn-outline text-lg px-8 py-3">
                <Search className="w-5 h-5 mr-2 inline" />
                Verify Watermark
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Revolutionary Watermarking Technology
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our semantic-aware system goes beyond simple ownership markers to create 
              comprehensive digital fingerprints that protect against sophisticated tampering.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="card text-center">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Icon className="w-6 h-6 text-primary-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Simple steps to protect your digital content with advanced watermarking technology.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                <div className="card text-center">
                  <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-lg font-bold">
                    {step.number}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {step.title}
                  </h3>
                  <p className="text-gray-600">
                    {step.description}
                  </p>
                </div>
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 w-8 h-0.5 bg-primary-200 transform -translate-y-1/2"></div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Ready to Protect Your Images?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-3xl mx-auto">
            Start creating tamper-resistant watermarks for your digital assets today.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/create" className="bg-white text-primary-600 hover:bg-gray-100 font-medium py-3 px-8 rounded-lg transition-colors duration-200">
              Get Started Now
            </Link>
            <Link to="/verify" className="border border-white text-white hover:bg-white hover:text-primary-600 font-medium py-3 px-8 rounded-lg transition-colors duration-200">
              Verify Existing Watermark
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">PixelLedger</span>
            </div>
            <p className="text-gray-400 mb-4">
              Semantic-aware digital watermarking with blockchain binding
            </p>
            <p className="text-sm text-gray-500">
              © 2024 PixelLedger. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
