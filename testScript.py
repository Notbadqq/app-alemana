import pg

print("Iniciando proceso:")
f = open("/app/text.txt", "a")
f.write("Intentando iniciar\n------------\n")
conn = pg.DB(host='mydb', user='postgres', passwd='postgres', dbname='data')

result = conn.query("SELECT description_nombre FROM cas_hiba LIMIT 10")

for desc in result.getresult() :
    for datos in desc:
        f.write(datos)
        f.write("\n")

conn.close()
f.write("---------\nFinalizado\n")
f.close
print("Listo")