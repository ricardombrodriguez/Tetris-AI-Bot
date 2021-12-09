total=0
input="results.txt"
while IFS= read -r line
do
  total=$((total + line))
done < "$input"
echo $((total / 10)) >> "media.txt"

eval "$(ps aux | grep "python.*\.py" | awk '// {printf "kill -9 " $2 "\n"}')"