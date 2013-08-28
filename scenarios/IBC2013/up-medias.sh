> 'medias.csv'
find ../../medias/EBU/ -type f | while read media
do
  path=$(basename $(dirname "$media"))
  name=$(basename "$media")
  name=$(echo $path $name | sed 's: :_:g')
  title=$(basename "$media" | cut -d'.' -f1)
  echo "Adding $name"
  echo "$media;$name;$title" >> 'medias.csv'
done
