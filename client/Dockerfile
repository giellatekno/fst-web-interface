FROM nginx

COPY nginx.conf /etc/nginx/nginx.conf

COPY dist/ /var/www/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
