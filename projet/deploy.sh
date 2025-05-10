#docker buildx build --platform linux/amd64 -t flask-demo .
#
#gcloud run deploy flask-demo \
#  --image docker.io/bmosbah97/flask-demo:1.0 \
#  --platform managed \
#  --region europe-west1 \
#  --allow-unauthenticated