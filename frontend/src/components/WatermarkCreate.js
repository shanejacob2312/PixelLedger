import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Image, Download, Share2, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import toast from 'react-hot-toast';

const WatermarkCreate = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [metadata, setMetadata] = useState({
    owner_name: '',
    author: '',
    email: '',
    title: '',
    description: '',
    creation_date: new Date().toISOString().split('T')[0],
    copyright: '',
    license: 'CC BY-NC-ND 4.0',
    keywords: '',
    location: '',
    tags: ''
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [watermarkResult, setWatermarkResult] = useState(null);
  const [tamperDetected, setTamperDetected] = useState(false);

  const steps = [
    { number: 1, title: 'Upload Image', description: 'Select and upload your image' },
    { number: 2, title: 'Add Metadata', description: 'Provide ownership and copyright information' },
    { number: 3, title: 'Create Watermark', description: 'Generate and embed the watermark' },
    { number: 4, title: 'Download & Share', description: 'Get your watermarked image' }
  ];

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      // Validate file format
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        toast.error('Please upload a valid image file (JPEG, PNG, BMP, TIFF, or WebP)');
        return;
      }

      // Validate file size (max 100MB)
      if (file.size > 100 * 1024 * 1024) {
        toast.error('File size must be less than 100MB');
        return;
      }

      setUploadedImage(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);

      // Check for existing watermark
      checkExistingWatermark(file);
      
      toast.success('Image uploaded successfully!');
    }
  };

  const checkExistingWatermark = async (file) => {
    setIsProcessing(true);
    try {
      // Simulate watermark detection API call
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('/api/check-watermark', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      if (result.hasWatermark) {
        setTamperDetected(true);
        toast.error('This image already contains a watermark and may have been tampered with!');
      } else {
        setTamperDetected(false);
        setCurrentStep(2);
      }
    } catch (error) {
      console.error('Error checking watermark:', error);
      // Continue to next step if check fails
      setCurrentStep(2);
    } finally {
      setIsProcessing(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.tiff', '.webp']
    },
    multiple: false
  });

  const handleMetadataChange = (field, value) => {
    setMetadata(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCreateWatermark = async () => {
    if (!uploadedImage) {
      toast.error('Please upload an image first');
      return;
    }

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadedImage);
      formData.append('metadata', JSON.stringify(metadata));

      const response = await fetch('/api/create-watermark', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setWatermarkResult(result);
        setCurrentStep(4);
        toast.success('Watermark created successfully!');
      } else {
        toast.error(result.error || 'Failed to create watermark');
      }
    } catch (error) {
      console.error('Error creating watermark:', error);
      toast.error('Failed to create watermark. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    if (watermarkResult?.watermarked_image_url) {
      const link = document.createElement('a');
      link.href = watermarkResult.watermarked_image_url;
      link.download = `watermarked_${uploadedImage.name}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      toast.success('Image downloaded successfully!');
    }
  };

  const handleShare = () => {
    if (watermarkResult?.watermarked_image_url) {
      if (navigator.share) {
        navigator.share({
          title: 'Watermarked Image',
          text: 'Check out my watermarked image created with PixelLedger',
          url: watermarkResult.watermarked_image_url
        });
      } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(watermarkResult.watermarked_image_url);
        toast.success('Image URL copied to clipboard!');
      }
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Your Image</h2>
              <p className="text-gray-600">Select an image to create a semantic watermark</p>
            </div>

            {tamperDetected && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                  <div>
                    <h3 className="text-red-800 font-medium">Tampered Image Detected</h3>
                    <p className="text-red-700 text-sm mt-1">
                      This image already contains a watermark and may have been modified. 
                      Please use a different image or verify the existing watermark.
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
              }`}
            >
              <input {...getInputProps()} />
              {imagePreview ? (
                <div className="space-y-4">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="max-w-full max-h-64 mx-auto rounded-lg shadow-sm"
                  />
                  <div className="flex items-center justify-center space-x-2 text-green-600">
                    <CheckCircle className="w-5 h-5" />
                    <span className="font-medium">{uploadedImage.name}</span>
                  </div>
                  <p className="text-sm text-gray-500">
                    Click or drag to upload a different image
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                  <div>
                    <p className="text-lg font-medium text-gray-900">
                      {isDragActive ? 'Drop the image here' : 'Upload an image'}
                    </p>
                    <p className="text-gray-500 mt-1">
                      Drag and drop or click to select
                    </p>
                    <p className="text-sm text-gray-400 mt-2">
                      Supports JPEG, PNG, BMP, TIFF, WebP (max 100MB)
                    </p>
                  </div>
                </div>
              )}
            </div>

            {isProcessing && (
              <div className="flex items-center justify-center space-x-2 text-primary-600">
                <Loader className="w-5 h-5 animate-spin" />
                <span>Checking for existing watermarks...</span>
              </div>
            )}

            {uploadedImage && !tamperDetected && !isProcessing && (
              <div className="flex justify-center">
                <button
                  onClick={() => setCurrentStep(2)}
                  className="btn-primary"
                >
                  Continue to Metadata
                </button>
              </div>
            )}
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Add Metadata</h2>
              <p className="text-gray-600">Provide ownership and copyright information</p>
            </div>

            {imagePreview && (
              <div className="flex justify-center mb-6">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="max-w-xs rounded-lg shadow-sm"
                />
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="label">Owner Name *</label>
                <input
                  type="text"
                  value={metadata.owner_name}
                  onChange={(e) => handleMetadataChange('owner_name', e.target.value)}
                  className="input-field"
                  placeholder="Enter owner name"
                  required
                />
              </div>

              <div>
                <label className="label">Author/Creator *</label>
                <input
                  type="text"
                  value={metadata.author}
                  onChange={(e) => handleMetadataChange('author', e.target.value)}
                  className="input-field"
                  placeholder="Enter author name"
                  required
                />
              </div>

              <div>
                <label className="label">Email</label>
                <input
                  type="email"
                  value={metadata.email}
                  onChange={(e) => handleMetadataChange('email', e.target.value)}
                  className="input-field"
                  placeholder="Enter email address"
                />
              </div>

              <div>
                <label className="label">Creation Date *</label>
                <input
                  type="date"
                  value={metadata.creation_date}
                  onChange={(e) => handleMetadataChange('creation_date', e.target.value)}
                  className="input-field"
                  required
                />
              </div>

              <div className="md:col-span-2">
                <label className="label">Image Title *</label>
                <input
                  type="text"
                  value={metadata.title}
                  onChange={(e) => handleMetadataChange('title', e.target.value)}
                  className="input-field"
                  placeholder="Enter image title"
                  required
                />
              </div>

              <div className="md:col-span-2">
                <label className="label">Description</label>
                <textarea
                  value={metadata.description}
                  onChange={(e) => handleMetadataChange('description', e.target.value)}
                  className="input-field"
                  rows="3"
                  placeholder="Enter image description"
                />
              </div>

              <div>
                <label className="label">Copyright Notice *</label>
                <input
                  type="text"
                  value={metadata.copyright}
                  onChange={(e) => handleMetadataChange('copyright', e.target.value)}
                  className="input-field"
                  placeholder="© 2024 Owner Name. All rights reserved."
                  required
                />
              </div>

              <div>
                <label className="label">License</label>
                <select
                  value={metadata.license}
                  onChange={(e) => handleMetadataChange('license', e.target.value)}
                  className="input-field"
                >
                  <option value="CC BY-NC-ND 4.0">CC BY-NC-ND 4.0</option>
                  <option value="CC BY 4.0">CC BY 4.0</option>
                  <option value="CC BY-SA 4.0">CC BY-SA 4.0</option>
                  <option value="All Rights Reserved">All Rights Reserved</option>
                </select>
              </div>

              <div>
                <label className="label">Keywords</label>
                <input
                  type="text"
                  value={metadata.keywords}
                  onChange={(e) => handleMetadataChange('keywords', e.target.value)}
                  className="input-field"
                  placeholder="Enter keywords (comma-separated)"
                />
              </div>

              <div>
                <label className="label">Location</label>
                <input
                  type="text"
                  value={metadata.location}
                  onChange={(e) => handleMetadataChange('location', e.target.value)}
                  className="input-field"
                  placeholder="Enter location"
                />
              </div>
            </div>

            <div className="flex justify-between">
              <button
                onClick={() => setCurrentStep(1)}
                className="btn-secondary"
              >
                Back
              </button>
              <button
                onClick={() => setCurrentStep(3)}
                className="btn-primary"
                disabled={!metadata.owner_name || !metadata.author || !metadata.title || !metadata.copyright}
              >
                Continue to Watermark Creation
              </button>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Create Watermark</h2>
              <p className="text-gray-600">Generate and embed the semantic watermark</p>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Watermark Summary</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Image:</span>
                  <span className="font-medium">{uploadedImage.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Owner:</span>
                  <span className="font-medium">{metadata.owner_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Author:</span>
                  <span className="font-medium">{metadata.author}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Title:</span>
                  <span className="font-medium">{metadata.title}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">License:</span>
                  <span className="font-medium">{metadata.license}</span>
                </div>
              </div>
            </div>

            <div className="text-center">
              <button
                onClick={handleCreateWatermark}
                disabled={isProcessing}
                className="btn-primary text-lg px-8 py-3"
              >
                {isProcessing ? (
                  <>
                    <Loader className="w-5 h-5 mr-2 inline animate-spin" />
                    Creating Watermark...
                  </>
                ) : (
                  'Create Watermark'
                )}
              </button>
            </div>

            <div className="flex justify-center">
              <button
                onClick={() => setCurrentStep(2)}
                className="btn-secondary"
              >
                Back to Metadata
              </button>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Watermark Created!</h2>
              <p className="text-gray-600">Your image has been successfully watermarked</p>
            </div>

            {watermarkResult && (
              <div className="card">
                <div className="text-center mb-6">
                  <img
                    src={watermarkResult.watermarked_image_url}
                    alt="Watermarked"
                    className="max-w-full max-h-96 mx-auto rounded-lg shadow-sm"
                  />
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">Watermark Details</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex items-center mb-2">
                        <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                        <span className="font-medium text-green-800">Semantic Context</span>
                      </div>
                      <p className="text-sm text-green-700">
                        Caption: {watermarkResult.semantic_context?.caption || 'Generated caption'}
                      </p>
                      <p className="text-sm text-green-700">
                        Objects: {watermarkResult.semantic_context?.detected_objects?.length || 0} detected
                      </p>
                    </div>

                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="flex items-center mb-2">
                        <Image className="w-5 h-5 text-blue-600 mr-2" />
                        <span className="font-medium text-blue-800">Perceptual Hash</span>
                      </div>
                      <p className="text-sm text-blue-700 font-mono">
                        {watermarkResult.phash?.substring(0, 16) || 'Generated hash'}...
                      </p>
                    </div>
                  </div>

                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">Capacity Usage</h4>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Used:</span>
                      <span className="font-medium">{watermarkResult.capacity_used} bits</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Total:</span>
                      <span className="font-medium">{watermarkResult.total_capacity} bits</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full" 
                        style={{ 
                          width: `${(watermarkResult.capacity_used / watermarkResult.total_capacity) * 100}%` 
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={handleDownload}
                className="btn-primary"
              >
                <Download className="w-5 h-5 mr-2 inline" />
                Download Image
              </button>
              <button
                onClick={handleShare}
                className="btn-outline"
              >
                <Share2 className="w-5 h-5 mr-2 inline" />
                Share Image
              </button>
            </div>

            <div className="text-center">
              <button
                onClick={() => {
                  setCurrentStep(1);
                  setUploadedImage(null);
                  setImagePreview(null);
                  setWatermarkResult(null);
                  setTamperDetected(false);
                }}
                className="btn-secondary"
              >
                Create Another Watermark
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  currentStep >= step.number
                    ? 'bg-primary-600 border-primary-600 text-white'
                    : 'border-gray-300 text-gray-500'
                }`}>
                  {currentStep > step.number ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    <span className="text-sm font-medium">{step.number}</span>
                  )}
                </div>
                <div className="ml-3 hidden sm:block">
                  <p className={`text-sm font-medium ${
                    currentStep >= step.number ? 'text-primary-600' : 'text-gray-500'
                  }`}>
                    {step.title}
                  </p>
                  <p className="text-xs text-gray-500">{step.description}</p>
                </div>
                {index < steps.length - 1 && (
                  <div className={`hidden sm:block w-16 h-0.5 mx-4 ${
                    currentStep > step.number ? 'bg-primary-600' : 'bg-gray-300'
                  }`}></div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="card">
          {renderStepContent()}
        </div>
      </div>
    </div>
  );
};

export default WatermarkCreate;
