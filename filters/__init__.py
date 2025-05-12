from loader import dp
from .RoleFilters import IsSuperAdmin, IsUser


if __name__ == "filters":
    dp.filters_factory.bind(IsSuperAdmin)
    dp.filters_factory.bind(IsUser)