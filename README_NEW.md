# Templates

Creating a template in *interactive mode*:

```ps1
pipeline template create --interactive
```

Listining all templates:

```ps1
pipeline template list:
```

Showing the details of a single template:

```ps1
pipeline template show my_template
```

Updating the description of a template:

```ps1
pipeline template update my_template --set-description "New description"
```

Deleting a template:

```ps1
pipeline template delete my_template
```

> There is no way to change the name or the parameters of a template.
