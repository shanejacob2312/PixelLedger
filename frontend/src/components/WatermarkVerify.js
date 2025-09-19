import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Search, AlertTriangle, CheckCircle, XCircle, Loader, Eye, Shield } from 'lucide-react';
import toast from 'react-hot-toast';

const WatermarkVerify = () => {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      // Validate file format
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        toast.error('Please upload a valid image file (JPEG, PNG, BMP, TIFF, or WebP)');
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error('File size must be less than 10MB');
        return;
      }

      setUploadedImage(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);

      toast.success('Image uploaded successfully!');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.bmp', '.tiff', '.webp']
    },
    multiple: false
  });

  const handleVerifyWatermark = async () => {
    if (!uploadedImage) {
      toast.error('Please upload an image first');
      return;
    }

    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadedImage);

      const response = await fetch('/api/verify-watermark', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setVerificationResult(result);
        toast.success('Watermark verification completed!');
      } else {
        setVerificationResult({
          success: false,
          error: result.error || 'No watermark found'
        });
        toast.error(result.error || 'No watermark found in this image');
      }
    } catch (error) {
      console.error('Error verifying watermark:', error);
      toast.error('Failed to verify watermark. Please try again.');
      setVerificationResult({
        success: false,
        error: 'Verification failed'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const renderVerificationResult = () => {
    if (!verificationResult) return null;

    if (!verificationResult.success) {
      return (
        <div className="card">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <XCircle className="w-8 h-8 text-red-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Watermark Found</h3>
            <p className="text-gray-600 mb-6">
              This image does not contain a PixelLedger watermark or the watermark could not be extracted.
            </p>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
                <div>
                  <h4 className="text-red-800 font-medium">Possible Reasons:</h4>
                  <ul className="text-red-700 text-sm mt-1 list-disc list-inside">
                    <li>Image was never watermarked with PixelLedger</li>
                    <li>Image has been heavily compressed or modified</li>
                    <li>Watermark was corrupted or removed</li>
                    <li>Image format is not supported</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    const { fingerprint, verification_results, drift_analysis, current_semantic_context, overall_authentic } = verificationResult;

    return (
      <div className="space-y-6">
        {/* Overall Status */}
        <div className="card">
          <div className="text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${
              overall_authentic ? 'bg-green-100' : 'bg-red-100'
            }`}>
              {overall_authentic ? (
                <CheckCircle className="w-8 h-8 text-green-600" />
              ) : (
                <XCircle className="w-8 h-8 text-red-600" />
              )}
            </div>
            <h3 className={`text-xl font-semibold mb-2 ${
              overall_authentic ? 'text-green-800' : 'text-red-800'
            }`}>
              {overall_authentic ? 'Image is Authentic' : 'Image May Be Tampered'}
            </h3>
            <p className={`text-sm ${
              overall_authentic ? 'text-green-600' : 'text-red-600'
            }`}>
              {overall_authentic 
                ? 'The watermark is valid and no tampering was detected'
                : 'Watermark verification failed or tampering was detected'
              }
            </p>
          </div>
        </div>

        {/* Verification Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Shield className="w-5 h-5 mr-2" />
              Verification Results
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Fingerprint Valid:</span>
                <span className={`font-medium ${verification_results.fingerprint_valid ? 'text-green-600' : 'text-red-600'}`}>
                  {verification_results.fingerprint_valid ? '✓ Valid' : '✗ Invalid'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Image Hash:</span>
                <span className={`font-medium ${verification_results.image_hash_valid ? 'text-green-600' : 'text-red-600'}`}>
                  {verification_results.image_hash_valid ? '✓ Valid' : '✗ Invalid'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Metadata Hash:</span>
                <span className={`font-medium ${verification_results.metadata_hash_valid ? 'text-green-600' : 'text-red-600'}`}>
                  {verification_results.metadata_hash_valid ? '✓ Valid' : '✗ Invalid'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Features Hash:</span>
                <span className={`font-medium ${verification_results.features_hash_valid ? 'text-green-600' : 'text-red-600'}`}>
                  {verification_results.features_hash_valid ? '✓ Valid' : '✗ Invalid'}
                </span>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Eye className="w-5 h-5 mr-2" />
              Semantic Analysis
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Drift Detected:</span>
                <span className={`font-medium ${drift_analysis.drift_detected ? 'text-red-600' : 'text-green-600'}`}>
                  {drift_analysis.drift_detected ? '⚠ Detected' : '✓ No Drift'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Caption Changed:</span>
                <span className={`font-medium ${drift_analysis.caption_changed ? 'text-red-600' : 'text-green-600'}`}>
                  {drift_analysis.caption_changed ? '⚠ Changed' : '✓ Unchanged'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Objects Changed:</span>
                <span className={`font-medium ${drift_analysis.objects_changed ? 'text-red-600' : 'text-green-600'}`}>
                  {drift_analysis.objects_changed ? '⚠ Changed' : '✓ Unchanged'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Semantic Hash:</span>
                <span className={`font-medium ${drift_analysis.semantic_hash_changed ? 'text-red-600' : 'text-green-600'}`}>
                  {drift_analysis.semantic_hash_changed ? '⚠ Changed' : '✓ Unchanged'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Embedded Information */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Embedded Information</h3>
          
          {fingerprint?.data && (
            <div className="space-y-6">
              {/* Metadata */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Ownership Details</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <span className="text-gray-600">Owner:</span>
                    <span className="font-medium ml-2">{fingerprint.data.metadata?.owner_name || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Author:</span>
                    <span className="font-medium ml-2">{fingerprint.data.metadata?.author || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Title:</span>
                    <span className="font-medium ml-2">{fingerprint.data.metadata?.title || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Creation Date:</span>
                    <span className="font-medium ml-2">{fingerprint.data.metadata?.creation_date || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Copyright:</span>
                    <span className="font-medium ml-2">{fingerprint.data.metadata?.copyright || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">License:</span>
                    <span className="font-medium ml-2">{fingerprint.data.metadata?.license || 'N/A'}</span>
                  </div>
                </div>
              </div>

              {/* Semantic Context */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Semantic Context</h4>
                <div className="space-y-3">
                  <div>
                    <span className="text-gray-600">AI Generated Caption:</span>
                    <p className="font-medium mt-1 bg-gray-50 p-3 rounded-lg">
                      {fingerprint.data.semantic_context?.caption || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600">Detected Objects:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {fingerprint.data.semantic_context?.detected_objects?.map((obj, index) => (
                        <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                          {obj}
                        </span>
                      )) || <span className="text-gray-500">None detected</span>}
                    </div>
                  </div>
                </div>
              </div>

              {/* Technical Details */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Technical Details</h4>
                <div className="space-y-2">
                  <div>
                    <span className="text-gray-600">Watermark Version:</span>
                    <span className="font-medium ml-2">{fingerprint.version || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Creation Timestamp:</span>
                    <span className="font-medium ml-2">{fingerprint.timestamp || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Perceptual Hash:</span>
                    <span className="font-medium ml-2 font-mono text-sm">
                      {fingerprint.data.phash?.substring(0, 16) || 'N/A'}...
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Blockchain Hash:</span>
                    <span className="font-medium ml-2 font-mono text-sm">
                      {fingerprint.blockchain_hash?.substring(0, 16) || 'N/A'}...
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Current vs Original Comparison */}
        {drift_analysis.drift_detected && (
          <div className="card">
            <h3 className="text-lg font-semibold text-red-800 mb-4 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              Content Changes Detected
            </h3>
            <div className="space-y-4">
              {drift_analysis.caption_changed && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Caption Changes:</h4>
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-sm text-red-800">
                      The AI-generated caption has changed, indicating potential content modification.
                    </p>
                  </div>
                </div>
              )}
              {drift_analysis.objects_changed && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Object Detection Changes:</h4>
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-sm text-red-800">
                      Detected objects have changed, suggesting image content has been modified.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Verify Watermark</h1>
          <p className="text-xl text-gray-600">
            Upload an image to check if it contains a PixelLedger watermark and verify its authenticity
          </p>
        </div>

        {/* Upload Section */}
        <div className="card mb-8">
          <div className="text-center mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Upload Image to Verify</h2>
            <p className="text-gray-600">Select an image to check for embedded watermarks</p>
          </div>

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
                    Supports JPEG, PNG, BMP, TIFF, WebP (max 10MB)
                  </p>
                </div>
              </div>
            )}
          </div>

          {uploadedImage && (
            <div className="text-center mt-6">
              <button
                onClick={handleVerifyWatermark}
                disabled={isProcessing}
                className="btn-primary text-lg px-8 py-3"
              >
                {isProcessing ? (
                  <>
                    <Loader className="w-5 h-5 mr-2 inline animate-spin" />
                    Verifying Watermark...
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5 mr-2 inline" />
                    Verify Watermark
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Verification Results */}
        {renderVerificationResult()}

        {/* Reset Button */}
        {verificationResult && (
          <div className="text-center mt-8">
            <button
              onClick={() => {
                setUploadedImage(null);
                setImagePreview(null);
                setVerificationResult(null);
              }}
              className="btn-secondary"
            >
              Verify Another Image
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default WatermarkVerify;
