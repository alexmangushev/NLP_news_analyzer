# f1 = open('t.txt', 'r')
f = open('tt.txt', 'w')
# data = f1.readle();


with open ('t.txt', 'r') as i:
    for p in i:
        print(p)
        if p.find("lemma") > -1:
            f.write(p[7:-2] + "\n")

    


# dostopr "казанский_кафедральный_собор"
# {
# key="Казанский кафедральный собор"
# lemma="Казанский_кафедральный_собор"
# }
