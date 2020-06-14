import twint

c = twint.Config()
c.Username = "visakanv"
c.Database = c.Username + ".db"

twint.run.Search(c)
