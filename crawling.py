from datetime import date
from crawlers import InterparkCrawler


def main():
    interpark_crawler = InterparkCrawler()
    concert_goods_list = interpark_crawler.crawl_performance_list(
        date.today(), kind_code=interpark_crawler.INTERPARK_CONSERT_KIND_CODE
    )
    musical_goods_list = interpark_crawler.crawl_performance_list(
        date.today(), kind_code=interpark_crawler.INTERPARK_MUSICAL_KIND_CODE
    )
    print("concert: ", interpark_crawler.crawl_performance(concert_goods_list[-1]))
    print("musical: ", interpark_crawler.crawl_performance(musical_goods_list[-1]))


if __name__ == "__main__":
    main()
