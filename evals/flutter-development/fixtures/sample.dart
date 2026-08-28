Future<void> save(BuildContext context) async {
  await repository.persist();
  Navigator.of(context).pop();
}
