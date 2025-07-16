source venv-piper/bin/activate

cat inputs/hello_world.txt | piper \
--data-dir ./voices/ \
--download-dir ./voices/ \
--model en_US-lessac-medium \
--output_file welcome.wav