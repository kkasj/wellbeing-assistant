abstract class LoginEvent {}

class LoginUsernameChanged extends LoginEvent {
  final String email;

  LoginUsernameChanged({required this.email});
}

class LoginPasswordChanged extends LoginEvent {
  final String password;

  LoginPasswordChanged({required this.password});
}

class LoginSubmitted extends LoginEvent {}
