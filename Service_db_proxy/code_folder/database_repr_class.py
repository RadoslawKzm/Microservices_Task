class ReprClass:
    def __repr__(self):
        return f"""name={self.__tablename__},
        {','.join(f'{k}={v}' for k, v in self.__dict__.items() if not k.startswith('_'))}"""
