import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../utils/constants.dart';

class CameraCaptureScreen extends StatefulWidget {
  final String title;

  const CameraCaptureScreen({
    super.key,
    this.title = 'Take Photo',
  });

  @override
  State<CameraCaptureScreen> createState() => _CameraCaptureScreenState();
}

class _CameraCaptureScreenState extends State<CameraCaptureScreen> with WidgetsBindingObserver {
  List<CameraDescription> _cameras = [];
  CameraController? _controller;
  int _selectedCameraIndex = 0;
  bool _isInitializing = true;
  bool _isCapturing = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initCamera();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _controller?.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final CameraController? cameraController = _controller;
    if (cameraController == null || !cameraController.value.isInitialized) {
      return;
    }

    if (state == AppLifecycleState.inactive) {
      cameraController.dispose();
    } else if (state == AppLifecycleState.resumed) {
      _startCameraController(cameraController.description);
    }
  }

  Future<void> _initCamera() async {
    try {
      _cameras = await availableCameras();
      if (_cameras.isEmpty) {
        setState(() {
          _isInitializing = false;
          _errorMessage = 'No camera found on this device.';
        });
        return;
      }

      // Default to back camera for clothing photos if available, or first camera (webcam)
      int defaultIndex = 0;
      for (int i = 0; i < _cameras.length; i++) {
        if (_cameras[i].lensDirection == CameraLensDirection.back) {
          defaultIndex = i;
          break;
        }
      }

      _selectedCameraIndex = defaultIndex;
      await _startCameraController(_cameras[_selectedCameraIndex]);
    } catch (e) {
      setState(() {
        _isInitializing = false;
        _errorMessage = 'Could not access camera: $e';
      });
    }
  }

  Future<void> _startCameraController(CameraDescription cameraDescription) async {
    final CameraController cameraController = CameraController(
      cameraDescription,
      ResolutionPreset.high,
      enableAudio: false,
    );

    _controller = cameraController;

    try {
      await cameraController.initialize();
      if (mounted) {
        setState(() {
          _isInitializing = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isInitializing = false;
          _errorMessage = 'Failed to initialize camera preview: $e';
        });
      }
    }
  }

  Future<void> _switchCamera() async {
    if (_cameras.length <= 1) return;
    final newIndex = (_selectedCameraIndex + 1) % _cameras.length;
    setState(() {
      _selectedCameraIndex = newIndex;
      _isInitializing = true;
    });
    await _controller?.dispose();
    await _startCameraController(_cameras[_selectedCameraIndex]);
  }

  Future<void> _takePicture() async {
    final CameraController? cameraController = _controller;
    if (cameraController == null || !cameraController.value.isInitialized || _isCapturing) {
      return;
    }

    try {
      setState(() {
        _isCapturing = true;
      });

      final XFile file = await cameraController.takePicture();
      final Uint8List bytes = await file.readAsBytes();

      if (mounted) {
        Navigator.pop(context, {'bytes': bytes, 'name': file.name});
      }
    } catch (e) {
      setState(() {
        _isCapturing = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to capture photo: $e'), backgroundColor: AppColors.error),
        );
      }
    }
  }

  Future<void> _fallbackToGallery() async {
    final picker = ImagePicker();
    try {
      final file = await picker.pickImage(source: ImageSource.gallery, maxWidth: 1600, maxHeight: 1600, imageQuality: 88);
      if (file != null && mounted) {
        final bytes = await file.readAsBytes();
        Navigator.pop(context, {'bytes': bytes, 'name': file.name});
      }
    } catch (e) {
      debugPrint('Gallery error: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: _isInitializing
            ? const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(color: AppColors.accent),
                    SizedBox(height: 16),
                    Text(
                      'Opening camera...',
                      style: TextStyle(color: Colors.white, fontSize: 16),
                    ),
                  ],
                ),
              )
            : _errorMessage != null
                ? Center(
                    child: Padding(
                      padding: const EdgeInsets.all(28.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.videocam_off_outlined, color: AppColors.accent, size: 64),
                          const SizedBox(height: 18),
                          Text(
                            _errorMessage!,
                            textAlign: TextAlign.center,
                            style: const TextStyle(color: Colors.white, fontSize: 16),
                          ),
                          const SizedBox(height: 10),
                          const Text(
                            'Please allow camera permission in your browser or device settings, or choose a file from your device.',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.white70, fontSize: 13),
                          ),
                          const SizedBox(height: 24),
                          ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.accent,
                              foregroundColor: Colors.black,
                              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                            ),
                            icon: const Icon(Icons.photo_library_outlined),
                            label: const Text('Select from Gallery / Files'),
                            onPressed: _fallbackToGallery,
                          ),
                          const SizedBox(height: 12),
                          TextButton(
                            onPressed: () => Navigator.pop(context),
                            child: const Text('Go Back', style: TextStyle(color: Colors.white70)),
                          ),
                        ],
                      ),
                    ),
                  )
                : Stack(
                    fit: StackFit.expand,
                    children: [
                      // Live Camera Viewfinder
                      Center(
                        child: CameraPreview(_controller!),
                      ),

                      // Framing overlay guide
                      Center(
                        child: Container(
                          width: MediaQuery.of(context).size.width * 0.85,
                          height: MediaQuery.of(context).size.height * 0.65,
                          decoration: BoxDecoration(
                            border: Border.all(color: Colors.white.withValues(alpha: 0.35), width: 2),
                            borderRadius: BorderRadius.circular(16),
                          ),
                        ),
                      ),

                      // Top Bar
                      Positioned(
                        top: 16,
                        left: 16,
                        right: 16,
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            CircleAvatar(
                              backgroundColor: Colors.black54,
                              child: IconButton(
                                icon: const Icon(Icons.close, color: Colors.white),
                                onPressed: () => Navigator.pop(context),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                              decoration: BoxDecoration(
                                color: Colors.black54,
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Text(
                                widget.title,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w600,
                                  fontSize: 14,
                                ),
                              ),
                            ),
                            if (_cameras.length > 1)
                              CircleAvatar(
                                backgroundColor: Colors.black54,
                                child: IconButton(
                                  icon: const Icon(Icons.flip_camera_ios_outlined, color: Colors.white),
                                  onPressed: _switchCamera,
                                ),
                              )
                            else
                              const SizedBox(width: 40),
                          ],
                        ),
                      ),

                      // Bottom Control Bar with Shutter Button
                      Positioned(
                        bottom: 30,
                        left: 0,
                        right: 0,
                        child: Column(
                          children: [
                            const Text(
                              'Position garment inside frame and snap photo',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 13,
                                shadows: [Shadow(blurRadius: 4, color: Colors.black)],
                              ),
                            ),
                            const SizedBox(height: 18),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                              children: [
                                // Gallery option button
                                IconButton(
                                  icon: const Icon(Icons.photo_library, color: Colors.white, size: 28),
                                  tooltip: 'Choose from files',
                                  onPressed: _fallbackToGallery,
                                ),

                                // Primary Shutter Button
                                GestureDetector(
                                  onTap: _isCapturing ? null : _takePicture,
                                  child: Container(
                                    width: 76,
                                    height: 76,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      border: Border.all(color: Colors.white, width: 4),
                                    ),
                                    child: Center(
                                      child: _isCapturing
                                          ? const CircularProgressIndicator(color: AppColors.accent)
                                          : Container(
                                              width: 60,
                                              height: 60,
                                              decoration: const BoxDecoration(
                                                color: Colors.white,
                                                shape: BoxShape.circle,
                                              ),
                                            ),
                                    ),
                                  ),
                                ),

                                const SizedBox(width: 48), // spacer for balance
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
      ),
    );
  }
}
