# How to update specification schemas

## Initial setup

```
# add remote
$ git remote add gltf-spec git@github.com:KhronosGroup/glTF.git
$ git fetch gltf-spec

# split json schema history
$ git checkout -b gltf/master gltf-spec/master
$ git subtree split -P specification/2.0/schema -b split-schemas

# add splitted subtree
$ git checkout <origin/branch> ## NOT MASTER
$ git subtree add --squash -P schemas/specification/core split-schemas

# remove temp branch
git branch -D split-schemas
```

## Subsequent updates

given the setup from earlier:

```
# split json schema history (again)
$ git checkout -b gltf/master gltf-spec/master
$ git subtree split -P specification/2.0/schema -b split-schemas

# merge updated subtree
$ git subtree merge --squash -P schemas/specification/core split-schemas

# remove temp branch
git branch -D split-schemas
```
