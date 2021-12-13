while read one;
do
    echo $one
    wget $one -P $2
done < $1