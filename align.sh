DATA=zh_en_data/train
MODEL=hmm_models

python3 src/align.py \
  $DATA.zh $DATA.en $DATA.align \
  $MODEL/zh_en_hmm.json $MODEL/en_zh_hmm.json
