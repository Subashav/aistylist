import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/saved_results_provider.dart';
import '../models/saved_result_model.dart';
import '../app_config.dart';
import '../utils/constants.dart';
import '../utils/responsive_builder.dart';
import '../widgets/responsive_scaffold.dart';
import '../widgets/app_button.dart';

class SavedResultsScreen extends StatefulWidget {
  const SavedResultsScreen({super.key});

  @override
  State<SavedResultsScreen> createState() => _SavedResultsScreenState();
}

class _SavedResultsScreenState extends State<SavedResultsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final savedProvider = Provider.of<SavedResultsProvider>(context, listen: false);
      if (authProvider.token != null) {
        savedProvider.fetchSavedResults(authProvider.token!);
      }
    });
  }

  Future<void> _confirmDelete(BuildContext context, SavedResultModel item) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Saved Look?'),
        content: Text('Are you sure you want to remove "${item.colourShade} ${item.clothingType}" from your wardrobe?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final savedProvider = Provider.of<SavedResultsProvider>(context, listen: false);
      await savedProvider.deleteResult(item.id, authProvider.token ?? '');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Saved look removed from wardrobe.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final savedProvider = Provider.of<SavedResultsProvider>(context);

    return ResponsiveScaffold(
      currentIndex: 1,
      title: 'My Saved Wardrobe',
      body: savedProvider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : savedProvider.savedItems.isEmpty
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(32),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 80,
                          height: 80,
                          decoration: BoxDecoration(
                            color: AppColors.primary.withOpacity(0.06),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(
                            Icons.checkroom_outlined,
                            size: 40,
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 20),
                        const Text(
                          'Your Wardrobe is Empty',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w700,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'Analyze and save outfits to build your personalised color harmony lookbook.',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 14, color: AppColors.textSecondary),
                        ),
                        const SizedBox(height: 24),
                        AppButton(
                          text: 'Analyze Garment Now',
                          icon: Icons.photo_camera_outlined,
                          onPressed: () => Navigator.pushReplacementNamed(context, AppRoutes.home),
                        ),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: () async {
                    final authProvider = Provider.of<AuthProvider>(context, listen: false);
                    if (authProvider.token != null) {
                      await savedProvider.fetchSavedResults(authProvider.token!);
                    }
                  },
                  child: ResponsiveBuilder(
                    mobile: (ctx) => ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: savedProvider.savedItems.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 12),
                      itemBuilder: (ctx, idx) => _buildItemCard(savedProvider.savedItems[idx]),
                    ),
                    desktop: (ctx) => GridView.builder(
                      padding: const EdgeInsets.all(24),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        crossAxisSpacing: 16,
                        mainAxisSpacing: 16,
                        childAspectRatio: 2.2,
                      ),
                      itemCount: savedProvider.savedItems.length,
                      itemBuilder: (ctx, idx) => _buildItemCard(savedProvider.savedItems[idx]),
                    ),
                  ),
                ),
    );
  }

  Widget _buildItemCard(SavedResultModel item) {
    final color = item.toFlutterColor();
    final imageUrl = AppConfig.buildImageUrl(item.clothingImage);

    return InkWell(
      onTap: () {
        Navigator.pushNamed(
          context,
          AppRoutes.savedResultDetail,
          arguments: item,
        );
      },
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.border),
          boxShadow: const [
            BoxShadow(
              color: AppColors.cardShadow,
              blurRadius: 8,
              offset: Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            // Clothing Image or Color placeholder
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: Colors.black12,
                borderRadius: BorderRadius.circular(12),
              ),
              clipBehavior: Clip.antiAlias,
              child: imageUrl.isNotEmpty
                  ? Image.network(
                      imageUrl,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => Container(
                        color: color,
                        child: const Icon(Icons.checkroom, color: Colors.white),
                      ),
                    )
                  : Container(color: color),
            ),
            const SizedBox(width: 14),
            // Information
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 12,
                        height: 12,
                        decoration: BoxDecoration(
                          color: color,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.black26),
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        item.clothingType,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    item.colourShade,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${item.recommendations.length} Matching Swatches',
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            IconButton(
              icon: const Icon(Icons.delete_outline, color: AppColors.error, size: 20),
              tooltip: 'Delete Look',
              onPressed: () => _confirmDelete(context, item),
            ),
          ],
        ),
      ),
    );
  }
}
