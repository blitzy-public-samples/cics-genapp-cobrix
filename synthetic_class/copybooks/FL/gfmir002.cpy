******************************************************************
*  COPYBOOK  : GFMIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : MI
******************************************************************
 01  RT-FMI-RATING.

          03 RT-FMI-TERRITORY-CODE            PIC X(3).
          03 RT-FMI-CLASS-CODE                PIC X(4).
          03 RT-FMI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FMI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FMI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FMI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FMI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FMI-RATED-PREMIUM             PIC 9(9)V9(2).
