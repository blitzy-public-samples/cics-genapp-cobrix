******************************************************************
*  COPYBOOK  : GFHIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : HI
******************************************************************
 01  RT-FHI-RATING.

          03 RT-FHI-TERRITORY-CODE            PIC X(3).
          03 RT-FHI-CLASS-CODE                PIC X(4).
          03 RT-FHI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FHI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FHI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FHI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FHI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FHI-RATED-PREMIUM             PIC 9(9)V9(2).
