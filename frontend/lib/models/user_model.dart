class UserModel {
  final int id;
  final String fullName;
  final String email;
  final String? profileImage;
  final String createdAt;

  UserModel({
    required this.id,
    required this.fullName,
    required this.email,
    this.profileImage,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as int,
      fullName: json['full_name'] as String,
      email: json['email'] as String,
      profileImage: json['profile_image'] as String?,
      createdAt: json['created_at'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'full_name': fullName,
      'email': email,
      'profile_image': profileImage,
      'created_at': createdAt,
    };
  }
}
