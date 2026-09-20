import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../utils/responsive_builder.dart';

class ResponsiveScaffold extends StatelessWidget {
  final int currentIndex;
  final Widget body;
  final String? title;
  final List<Widget>? actions;
  final Widget? floatingActionButton;

  const ResponsiveScaffold({
    super.key,
    required this.currentIndex,
    required this.body,
    this.title,
    this.actions,
    this.floatingActionButton,
  });

  void _onNavigation(BuildContext context, int index) {
    if (index == currentIndex) return;
    switch (index) {
      case 0:
        Navigator.pushReplacementNamed(context, AppRoutes.home);
        break;
      case 1:
        Navigator.pushReplacementNamed(context, AppRoutes.savedResults);
        break;
      case 2:
        Navigator.pushReplacementNamed(context, AppRoutes.profile);
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDesktop = Responsive.isDesktop(context) || Responsive.isTablet(context);

    if (isDesktop) {
      return Scaffold(
        appBar: AppBar(
          title: Row(
            children: [
              const Icon(Icons.auto_awesome, color: AppColors.accent, size: 24),
              const SizedBox(width: 10),
              Text(
                AppStrings.appName,
                style: const TextStyle(fontWeight: FontWeight.w700, letterSpacing: -0.5),
              ),
              const SizedBox(width: 8),
              Text(
                '• ${AppStrings.appTagline}',
                style: const TextStyle(fontSize: 13, color: AppColors.textSecondary, fontWeight: FontWeight.normal),
              ),
            ],
          ),
          actions: actions,
        ),
        body: Row(
          children: [
            NavigationRail(
              selectedIndex: currentIndex,
              onDestinationSelected: (index) => _onNavigation(context, index),
              labelType: NavigationRailLabelType.all,
              backgroundColor: AppColors.surface,
              indicatorColor: AppColors.primary.withOpacity(0.1),
              selectedIconTheme: const IconThemeData(color: AppColors.primary),
              selectedLabelTextStyle: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.w700),
              unselectedIconTheme: const IconThemeData(color: AppColors.textSecondary),
              destinations: const [
                NavigationRailDestination(
                  icon: Icon(Icons.home_outlined),
                  selectedIcon: Icon(Icons.home),
                  label: Text('Home'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.bookmark_outline),
                  selectedIcon: Icon(Icons.bookmark),
                  label: Text('Wardrobe'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.person_outline),
                  selectedIcon: Icon(Icons.person),
                  label: Text('Profile'),
                ),
              ],
            ),
            const VerticalDivider(thickness: 1, width: 1, color: AppColors.border),
            Expanded(
              child: ConstrainedContent(
                child: body,
              ),
            ),
          ],
        ),
        floatingActionButton: floatingActionButton,
      );
    }

    // Mobile layout
    return Scaffold(
      appBar: AppBar(
        title: Text(
          title ?? AppStrings.appName,
          style: const TextStyle(fontWeight: FontWeight.w700),
        ),
        actions: actions,
      ),
      body: body,
      bottomNavigationBar: NavigationBar(
        selectedIndex: currentIndex,
        onDestinationSelected: (index) => _onNavigation(context, index),
        backgroundColor: AppColors.surface,
        indicatorColor: AppColors.primary.withOpacity(0.12),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home, color: AppColors.primary),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.bookmark_outline),
            selectedIcon: Icon(Icons.bookmark, color: AppColors.primary),
            label: 'Saved Looks',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person, color: AppColors.primary),
            label: 'Profile',
          ),
        ],
      ),
      floatingActionButton: floatingActionButton,
    );
  }
}
